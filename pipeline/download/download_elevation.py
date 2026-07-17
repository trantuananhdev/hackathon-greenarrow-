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

from pipeline.shared.data_contract import (
    TIMEZONE,
    validate_location_ids,
    validate_no_duplicate_keys,
    validate_timezone,
)


ELEVATION_URL = "https://api.open-meteo.com/v1/elevation"
ELEVATION_SOURCE = "copernicus_dem_90m"
MAX_COORDINATES_PER_REQUEST = 100


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def create_session() -> requests.Session:
    retry = Retry(
        total=5,
        backoff_factor=2,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET",),
        respect_retry_after_header=True,
    )
    session = requests.Session()
    session.mount("https://", HTTPAdapter(max_retries=retry))
    return session


def fetch_elevations(
    session: requests.Session,
    locations: pd.DataFrame,
) -> dict:
    if len(locations) > MAX_COORDINATES_PER_REQUEST:
        raise ValueError(
            f"Elevation API hỗ trợ tối đa {MAX_COORDINATES_PER_REQUEST} điểm"
        )
    response = session.get(
        ELEVATION_URL,
        params={
            "latitude": ",".join(locations["latitude"].astype(str)),
            "longitude": ",".join(locations["longitude"].astype(str)),
        },
        timeout=60,
    )
    response.raise_for_status()
    return response.json()


def build_location_features(
    locations: pd.DataFrame,
    payload: dict,
    retrieved_at: pd.Timestamp,
) -> pd.DataFrame:
    elevations = payload.get("elevation")
    if not isinstance(elevations, list) or len(elevations) != len(locations):
        raise ValueError(
            f"API trả {0 if elevations is None else len(elevations)} elevation "
            f"cho {len(locations)} location"
        )
    features = pd.DataFrame(
        {
            "location_id": locations["location_id"].astype(int).to_numpy(),
            "elevation_m": pd.to_numeric(elevations, errors="coerce"),
            "elevation_source": ELEVATION_SOURCE,
            "elevation_retrieved_at": retrieved_at,
        }
    )
    validate_location_features(
        features,
        set(locations["location_id"].astype(int)),
    )
    return features


def validate_location_features(
    frame: pd.DataFrame,
    expected_location_ids: set[int],
) -> None:
    required = {
        "location_id",
        "elevation_m",
        "elevation_source",
        "elevation_retrieved_at",
    }
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"Location features thiếu cột: {sorted(missing)}")
    validate_no_duplicate_keys(frame, ["location_id"])
    validate_location_ids(frame, expected_location_ids)
    validate_timezone(frame, "elevation_retrieved_at")
    if frame["elevation_m"].isna().any():
        raise ValueError("Elevation có giá trị rỗng")
    if not frame["elevation_m"].between(-500, 9_000).all():
        raise ValueError("Elevation nằm ngoài khoảng hợp lý -500..9000m")


def write_location_features(
    frame: pd.DataFrame,
    output_path: Path,
    locations_sha256: str,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = output_path.with_suffix(".parquet.tmp")
    frame.to_parquet(
        temporary_path,
        index=False,
        engine="pyarrow",
        compression="zstd",
    )
    written = pd.read_parquet(temporary_path)
    validate_location_features(
        written,
        set(frame["location_id"].astype(int)),
    )
    temporary_path.replace(output_path)

    manifest = {
        "dataset": "dien_bien_location_features",
        "source": "Open-Meteo Elevation API",
        "elevation_source": ELEVATION_SOURCE,
        "timezone": TIMEZONE,
        "locations": len(frame),
        "locations_sha256": locations_sha256,
        "retrieved_at": frame["elevation_retrieved_at"].iloc[0].isoformat(),
    }
    manifest_path = output_path.with_suffix(".manifest.json")
    temporary_manifest = manifest_path.with_suffix(".json.tmp")
    temporary_manifest.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    temporary_manifest.replace(manifest_path)


def download_elevation(
    locations_path: Path,
    output_path: Path,
    overwrite: bool = False,
) -> pd.DataFrame:
    locations = pd.read_parquet(locations_path).sort_values("location_id")
    locations_sha256 = file_sha256(locations_path)
    if output_path.exists() and not overwrite:
        existing = pd.read_parquet(output_path)
        validate_location_features(
            existing,
            set(locations["location_id"].astype(int)),
        )
        manifest_path = output_path.with_suffix(".manifest.json")
        if not manifest_path.exists():
            raise ValueError(
                "Location features cache thiếu manifest; chạy --overwrite"
            )
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("locations_sha256") != locations_sha256:
            raise ValueError(
                "Location features không khớp locations hiện tại; "
                "chạy --overwrite"
            )
        return existing

    payload = fetch_elevations(create_session(), locations)
    retrieved_at = pd.Timestamp.now(tz=TIMEZONE)
    features = build_location_features(locations, payload, retrieved_at)
    write_location_features(features, output_path, locations_sha256)
    return features


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Tải elevation cho các điểm hành chính Điện Biên."
    )
    parser.add_argument(
        "--locations",
        type=Path,
        default=Path("data/reference/dien_bien_locations.parquet"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/features/location_features.parquet"),
    )
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    locations = pd.read_parquet(args.locations)
    request_count = math.ceil(
        len(locations) / MAX_COORDINATES_PER_REQUEST
    )
    print(f"{len(locations)} địa điểm | {request_count} elevation request")
    if args.dry_run:
        return

    features = download_elevation(
        args.locations,
        args.output,
        args.overwrite,
    )
    print(f"Đã lưu {len(features)} location features -> {args.output}")


if __name__ == "__main__":
    main()
