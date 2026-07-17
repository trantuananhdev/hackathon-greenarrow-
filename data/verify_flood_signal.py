import argparse
import hashlib
import json
import sys
from pathlib import Path

import pandas as pd

try:
    from data.download_flood import (
        latest_complete_partition,
        validate_flood_part,
    )
    from data.flood_signal import build_flood_signals
except ModuleNotFoundError:
    from download_flood import latest_complete_partition, validate_flood_part
    from flood_signal import build_flood_signals

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify(
    river_points_path: Path,
    flood_root: Path,
    signals_path: Path,
) -> dict:
    points = pd.read_parquet(river_points_path)
    if points["river_point_id"].duplicated().any():
        raise ValueError("river_point_id bị trùng")
    if len(points) != 12 or points["osm_way_id"].nunique() != 3:
        raise ValueError("River point master phải có 12 điểm trên 3 OSM ways")
    if not points["point_name"].notna().all():
        raise ValueError("River points thiếu point_name")

    partition = latest_complete_partition(flood_root)
    manifest = json.loads(
        (partition / "_manifest.json").read_text(encoding="utf-8")
    )
    if manifest["river_points_sha256"] != file_sha256(river_points_path):
        raise ValueError("Flood manifest không khớp river_points hiện tại")
    part_paths = sorted(partition.glob("part-*.parquet"))
    expected_parts = (len(points) + manifest["batch_size"] - 1) // manifest["batch_size"]
    if len(part_paths) != expected_parts:
        raise ValueError("Số flood parts không khớp manifest")

    sorted_points = points.sort_values("river_point_id")
    frames = []
    for index, part_path in enumerate(part_paths):
        expected_points = sorted_points.iloc[
                index * manifest["batch_size"] :
                (index + 1) * manifest["batch_size"]
            ]
        part = pd.read_parquet(part_path)
        validate_flood_part(
            part,
            expected_points,
            manifest["forecast_days"],
            pd.Timestamp(manifest["snapshot_at"]),
            manifest["model"],
        )
        frames.append(part)
    flood = pd.concat(frames, ignore_index=True)
    if len(flood) != len(points) * manifest["forecast_days"]:
        raise ValueError("Tổng số flood rows không đúng")

    signal_manifest_path = signals_path.with_suffix(".manifest.json")
    signal_manifest = json.loads(
        signal_manifest_path.read_text(encoding="utf-8")
    )
    if signal_manifest["signal_version"] != "glofas-trend-1.0":
        raise ValueError("Signal manifest có version không hợp lệ")
    if signal_manifest["river_points_sha256"] != file_sha256(
        river_points_path
    ):
        raise ValueError("Signal manifest không khớp river points")
    flood_manifest_path = partition / "_manifest.json"
    if signal_manifest["source_manifest_sha256"] != file_sha256(
        flood_manifest_path
    ):
        raise ValueError("Signal manifest không khớp flood manifest")
    expected_part_hashes = {
        str(path): file_sha256(path)
        for path in part_paths
    }
    if signal_manifest["source_parts_sha256"] != expected_part_hashes:
        raise ValueError("Signal manifest không khớp nội dung flood parts")

    saved_signals = pd.read_parquet(signals_path).sort_values(
        "river_point_id"
    ).reset_index(drop=True)
    recomputed = build_flood_signals(flood).sort_values(
        "river_point_id"
    ).reset_index(drop=True)
    pd.testing.assert_frame_equal(saved_signals, recomputed)
    if saved_signals["is_official_warning"].any():
        raise ValueError("GloFAS signal không được gắn nhãn cảnh báo chính thức")
    if "severity" in saved_signals:
        raise ValueError("GloFAS signal chưa hiệu chỉnh không được có severity")
    if len(saved_signals) != signal_manifest["rows"]:
        raise ValueError("Signal row count không khớp manifest")
    if saved_signals["snapshot_at"].nunique() != 1 or str(
        saved_signals["snapshot_at"].iloc[0]
    ) != signal_manifest["snapshot_at"]:
        raise ValueError("Signal snapshot không khớp manifest")
    representative = saved_signals[
        saved_signals["is_representative_grid_cell"]
    ]
    if representative["grid_cell_id"].duplicated().any():
        raise ValueError("Representative GloFAS grid cell bị trùng")
    if len(representative) != saved_signals["grid_cell_id"].nunique():
        raise ValueError("Mỗi GloFAS grid cell phải có đúng một representative")

    result = {
        "river_points": len(points),
        "rivers": points["river_name"].nunique(),
        "flood_rows": len(flood),
        "parts": len(part_paths),
        "signals": len(saved_signals),
        "grid_cells": len(representative),
        "partition": str(partition),
    }
    print(
        "VERIFY PASS: "
        f"{result['river_points']} điểm / {result['rivers']} sông | "
        f"{result['flood_rows']} flood rows | {result['signals']} signals / "
        f"{result['grid_cells']} grid cells"
    )
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify P3 GloFAS flood signal.")
    parser.add_argument(
        "--river-points",
        type=Path,
        default=Path("data/river_points.parquet"),
    )
    parser.add_argument("--flood-root", type=Path, default=Path("data/flood"))
    parser.add_argument(
        "--signals",
        type=Path,
        default=Path("data/flood_signals.parquet"),
    )
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    verify(arguments.river_points, arguments.flood_root, arguments.signals)
