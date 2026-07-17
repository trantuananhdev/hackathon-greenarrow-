import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

try:
    from data.data_contract import TIMEZONE
except ModuleNotFoundError:
    from data_contract import TIMEZONE


OSM_API_ROOT = "https://api.openstreetmap.org/api/0.6"
OSM_ATTRIBUTION = "© OpenStreetMap contributors"
OSM_LICENSE_URL = "https://www.openstreetmap.org/copyright"
POINTS_PER_WAY = 4
TARGET_DISTANCE_FRACTIONS = (0.2, 0.4, 0.6, 0.8)
RIVER_WAYS = {
    279788696: "Nậm Rốm",
    67504081: "Nậm Mức",
    470292947: "Nậm Lay",
}


def way_source_url(way_id: int) -> str:
    return f"{OSM_API_ROOT}/way/{way_id}/full.json"


def payload_sha256(payload: dict) -> str:
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def create_session() -> requests.Session:
    retry = Retry(
        total=5,
        backoff_factor=2,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET",),
        respect_retry_after_header=True,
    )
    session = requests.Session()
    session.headers["User-Agent"] = "hackathon-greenarrow-data-pipeline/1.0"
    session.mount("https://", HTTPAdapter(max_retries=retry))
    return session


def fetch_way(session: requests.Session, way_id: int) -> dict:
    response = session.get(way_source_url(way_id), timeout=60)
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, dict):
        raise ValueError(f"OSM way {way_id} không trả về JSON object")
    return payload


def _haversine_km(
    first_latitude: float,
    first_longitude: float,
    second_latitude: float,
    second_longitude: float,
) -> float:
    radius_km = 6_371.0088
    first_latitude_rad = math.radians(first_latitude)
    second_latitude_rad = math.radians(second_latitude)
    delta_latitude = math.radians(second_latitude - first_latitude)
    delta_longitude = math.radians(second_longitude - first_longitude)
    haversine = (
        math.sin(delta_latitude / 2) ** 2
        + math.cos(first_latitude_rad)
        * math.cos(second_latitude_rad)
        * math.sin(delta_longitude / 2) ** 2
    )
    return 2 * radius_km * math.asin(min(1.0, math.sqrt(haversine)))


def _ordered_way_nodes(payload: dict, way_id: int) -> list[dict]:
    elements = payload.get("elements")
    if not isinstance(elements, list):
        raise ValueError(f"OSM way {way_id} thiếu elements")
    matching_ways = [
        element
        for element in elements
        if element.get("type") == "way" and element.get("id") == way_id
    ]
    if len(matching_ways) != 1:
        raise ValueError(
            f"OSM payload phải chứa đúng một way {way_id}, "
            f"nhận được {len(matching_ways)}"
        )
    node_ids = matching_ways[0].get("nodes")
    if not isinstance(node_ids, list):
        raise ValueError(f"OSM way {way_id} thiếu danh sách nodes")
    nodes_by_id = {
        element["id"]: element
        for element in elements
        if element.get("type") == "node"
        and "id" in element
        and "lat" in element
        and "lon" in element
    }
    missing_node_ids = [node_id for node_id in node_ids if node_id not in nodes_by_id]
    if missing_node_ids:
        raise ValueError(
            f"OSM way {way_id} thiếu {len(missing_node_ids)} node coordinates"
        )
    return [nodes_by_id[node_id] for node_id in node_ids]


def _select_interior_nodes(nodes: list[dict], way_id: int) -> list[tuple]:
    interior_count = len(nodes) - 2
    if interior_count < POINTS_PER_WAY:
        raise ValueError(
            f"OSM way {way_id} cần ít nhất {POINTS_PER_WAY} interior nodes, "
            f"chỉ có {max(0, interior_count)}"
        )

    cumulative_distances = [0.0]
    for previous, current in zip(nodes, nodes[1:]):
        segment_distance = _haversine_km(
            float(previous["lat"]),
            float(previous["lon"]),
            float(current["lat"]),
            float(current["lon"]),
        )
        cumulative_distances.append(cumulative_distances[-1] + segment_distance)
    total_distance = cumulative_distances[-1]
    if total_distance <= 0:
        raise ValueError(f"OSM way {way_id} có tổng chiều dài bằng 0")

    available_indices = set(range(1, len(nodes) - 1))
    selected_indices = []
    for target_fraction in TARGET_DISTANCE_FRACTIONS:
        target_distance = total_distance * target_fraction
        selected_index = min(
            available_indices,
            key=lambda index: (
                abs(cumulative_distances[index] - target_distance),
                index,
            ),
        )
        selected_indices.append(selected_index)
        available_indices.remove(selected_index)

    return [
        (
            nodes[index],
            cumulative_distances[index],
            cumulative_distances[index] / total_distance,
        )
        for index in sorted(selected_indices)
    ]


def build_river_points(
    payloads: dict[int, dict],
    river_ways: dict[int, str],
    retrieved_at: pd.Timestamp,
) -> pd.DataFrame:
    timestamp = pd.Timestamp(retrieved_at)
    if timestamp.tzinfo is None:
        raise ValueError("retrieved_at phải có timezone")
    timestamp = timestamp.tz_convert(TIMEZONE)

    rows = []
    for way_id, river_name in river_ways.items():
        if way_id not in payloads:
            raise ValueError(f"Thiếu OSM payload cho way {way_id}")
        nodes = _ordered_way_nodes(payloads[way_id], way_id)
        selected_nodes = _select_interior_nodes(nodes, way_id)
        for sequence, (node, distance_km, distance_fraction) in enumerate(
            selected_nodes,
            start=1,
        ):
            node_id = int(node["id"])
            rows.append(
                {
                    "river_point_id": f"osm-way-{way_id}-node-{node_id}",
                    "river_name": river_name,
                    "point_name": f"{river_name} {sequence:02d}",
                    "point_sequence": sequence,
                    "latitude": float(node["lat"]),
                    "longitude": float(node["lon"]),
                    "distance_from_way_start_km": distance_km,
                    "distance_fraction": distance_fraction,
                    "osm_way_id": int(way_id),
                    "osm_node_id": node_id,
                    "source": "OpenStreetMap",
                    "source_attribution": OSM_ATTRIBUTION,
                    "source_url": way_source_url(way_id),
                    "source_payload_sha256": payload_sha256(payloads[way_id]),
                    "retrieved_at": timestamp,
                }
            )
    frame = pd.DataFrame(rows)
    validate_river_points(frame, river_ways)
    return frame


def validate_river_points(
    frame: pd.DataFrame,
    river_ways: dict[int, str] = RIVER_WAYS,
) -> None:
    required_columns = {
        "river_point_id",
        "river_name",
        "point_name",
        "point_sequence",
        "latitude",
        "longitude",
        "distance_from_way_start_km",
        "distance_fraction",
        "osm_way_id",
        "osm_node_id",
        "source",
        "source_attribution",
        "source_url",
        "source_payload_sha256",
        "retrieved_at",
    }
    missing_columns = required_columns.difference(frame.columns)
    if missing_columns:
        raise ValueError(f"River points thiếu cột: {sorted(missing_columns)}")
    expected_rows = len(river_ways) * POINTS_PER_WAY
    if len(frame) != expected_rows:
        raise ValueError(
            f"River points phải có {expected_rows} dòng, nhận được {len(frame)}"
        )
    if frame["river_point_id"].duplicated().any():
        raise ValueError("river_point_id bị trùng")
    if frame[["latitude", "longitude"]].isna().any().any():
        raise ValueError("River point có tọa độ rỗng")
    if not frame["latitude"].between(-90, 90).all():
        raise ValueError("River point có latitude không hợp lệ")
    if not frame["longitude"].between(-180, 180).all():
        raise ValueError("River point có longitude không hợp lệ")
    if not frame["distance_fraction"].between(0, 1, inclusive="neither").all():
        raise ValueError("River point không nằm trong interior của way")
    if frame["retrieved_at"].dt.tz is None:
        raise ValueError("retrieved_at thiếu timezone")

    for way_id, river_name in river_ways.items():
        group = frame.loc[frame["osm_way_id"] == way_id]
        if len(group) != POINTS_PER_WAY:
            raise ValueError(
                f"OSM way {way_id} phải có {POINTS_PER_WAY} river points"
            )
        if group["river_name"].nunique() != 1 or group["river_name"].iloc[0] != river_name:
            raise ValueError(f"OSM way {way_id} không khớp river_name")
        if group["point_sequence"].tolist() != list(range(1, POINTS_PER_WAY + 1)):
            raise ValueError(f"OSM way {way_id} có point_sequence không hợp lệ")
        if not group["distance_fraction"].is_monotonic_increasing:
            raise ValueError(f"OSM way {way_id} có node order không tăng")


def write_river_points(
    frame: pd.DataFrame,
    output_path: Path,
    payloads: dict[int, dict],
) -> None:
    validate_river_points(frame)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_output = output_path.with_suffix(".parquet.tmp")
    frame.to_parquet(
        temporary_output,
        index=False,
        engine="pyarrow",
        compression="zstd",
    )
    written = pd.read_parquet(temporary_output)
    validate_river_points(written)
    temporary_output.replace(output_path)

    fingerprints = {
        str(way_id): payload_sha256(payloads[way_id])
        for way_id in RIVER_WAYS
    }
    combined_fingerprint = hashlib.sha256(
        json.dumps(
            fingerprints,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    manifest = {
        "dataset": "dien_bien_river_points",
        "source": "OpenStreetMap API",
        "source_attribution": OSM_ATTRIBUTION,
        "license": "ODbL 1.0",
        "license_url": OSM_LICENSE_URL,
        "timezone": TIMEZONE,
        "ways": len(RIVER_WAYS),
        "points_per_way": POINTS_PER_WAY,
        "points": len(frame),
        "osm_way_ids": list(RIVER_WAYS),
        "source_urls": {
            str(way_id): way_source_url(way_id)
            for way_id in RIVER_WAYS
        },
        "source_sha256_by_way": fingerprints,
        "source_fingerprint_sha256": combined_fingerprint,
        "retrieved_at": frame["retrieved_at"].iloc[0].isoformat(),
    }
    manifest_path = output_path.with_suffix(".manifest.json")
    temporary_manifest = manifest_path.with_suffix(".json.tmp")
    temporary_manifest.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    temporary_manifest.replace(manifest_path)


def download_river_points(output_path: Path) -> pd.DataFrame:
    session = create_session()
    payloads = {
        way_id: fetch_way(session, way_id)
        for way_id in RIVER_WAYS
    }
    retrieved_at = pd.Timestamp.now(tz=TIMEZONE)
    frame = build_river_points(payloads, RIVER_WAYS, retrieved_at)
    write_river_points(frame, output_path, payloads)
    return frame


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Tạo các điểm sông Điện Biên từ node thật của OpenStreetMap."
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/river_points.parquet"),
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    print(
        f"{len(RIVER_WAYS)} OSM ways | "
        f"{POINTS_PER_WAY} điểm/way | "
        f"{len(RIVER_WAYS) * POINTS_PER_WAY} điểm"
    )
    if args.dry_run:
        return
    frame = download_river_points(args.output)
    print(f"Đã lưu {len(frame)} river points -> {args.output}")


if __name__ == "__main__":
    main()
