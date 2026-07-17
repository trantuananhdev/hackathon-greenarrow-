import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


SELECTION_METHOD = "deterministic_farthest_point_v1"


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _pairwise_haversine(
    latitude: np.ndarray,
    longitude: np.ndarray,
) -> np.ndarray:
    lat = np.radians(latitude.astype(float))
    lon = np.radians(longitude.astype(float))
    delta_lat = lat[:, None] - lat[None, :]
    delta_lon = lon[:, None] - lon[None, :]
    value = (
        np.sin(delta_lat / 2) ** 2
        + np.cos(lat[:, None])
        * np.cos(lat[None, :])
        * np.sin(delta_lon / 2) ** 2
    )
    return 6371.0 * 2 * np.arcsin(np.sqrt(value))


def select_spatial_representatives(
    locations: pd.DataFrame,
    count: int = 12,
) -> pd.DataFrame:
    required = {"location_id", "latitude", "longitude"}
    if missing := required.difference(locations.columns):
        raise ValueError(f"Locations thiếu cột: {sorted(missing)}")
    if count <= 0 or count > len(locations):
        raise ValueError("count phải trong khoảng 1..số location")
    ordered = locations.sort_values("location_id").reset_index(drop=True)
    distances = _pairwise_haversine(
        ordered["latitude"].to_numpy(),
        ordered["longitude"].to_numpy(),
    )
    selected = [0]
    while len(selected) < count:
        minimum_distance = distances[:, selected].min(axis=1)
        minimum_distance[selected] = -1
        selected.append(int(np.argmax(minimum_distance)))
    result = ordered.iloc[selected].copy().reset_index(drop=True)
    result["selection_rank"] = range(1, len(result) + 1)
    result["selection_method"] = SELECTION_METHOD
    result["selection_purpose"] = (
        "province-level ERA5 context; not independent event labels"
    )
    return result


def build_event_locations(
    locations_path: Path,
    output_path: Path,
    count: int = 12,
) -> pd.DataFrame:
    selected = select_spatial_representatives(
        pd.read_parquet(locations_path),
        count,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_output = output_path.with_suffix(".parquet.tmp")
    selected.to_parquet(temporary_output, index=False, compression="zstd")
    pd.read_parquet(temporary_output)
    os.replace(temporary_output, output_path)
    manifest = {
        "dataset": "dien_bien_event_context_locations",
        "source_locations_sha256": file_sha256(locations_path),
        "rows": len(selected),
        "selection_method": SELECTION_METHOD,
        "selection_purpose": (
            "Spatial context for province-level events; never independent labels"
        ),
        "artifact_sha256": file_sha256(output_path),
    }
    manifest_path = output_path.with_suffix(".manifest.json")
    temporary_manifest = manifest_path.with_suffix(".json.tmp")
    temporary_manifest.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    os.replace(temporary_manifest, manifest_path)
    return selected


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Chọn điểm đại diện không gian cho ERA5 event context."
    )
    parser.add_argument(
        "--locations",
        type=Path,
        default=Path("data/dien_bien_locations.parquet"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/event_locations.parquet"),
    )
    parser.add_argument("--count", type=int, default=12)
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    result = build_event_locations(
        arguments.locations,
        arguments.output,
        arguments.count,
    )
    print(f"Đã chọn {len(result)} điểm đại diện -> {arguments.output}")
