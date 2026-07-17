import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

import pandas as pd

try:
    from data.download_flood import latest_complete_partition
except ModuleNotFoundError:
    from download_flood import latest_complete_partition

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


SIGNAL_VERSION = "glofas-trend-1.0"
REQUIRED_COLUMNS = {
    "river_point_id",
    "river_name",
    "point_name",
    "snapshot_at",
    "valid_date",
    "river_discharge",
    "river_discharge_p25",
    "river_discharge_p75",
    "grid_latitude",
    "grid_longitude",
    "model",
}


def _classify_trend(baseline: float, ending: float) -> tuple[str, float | None]:
    if baseline <= 0:
        return "baseline_unavailable", None
    change_percent = (ending - baseline) / baseline * 100
    if change_percent >= 100:
        return "sharply_rising", change_percent
    if change_percent >= 50:
        return "rising", change_percent
    if change_percent <= -30:
        return "falling", change_percent
    return "stable", change_percent


def build_flood_signals(frame: pd.DataFrame) -> pd.DataFrame:
    missing = REQUIRED_COLUMNS.difference(frame.columns)
    if missing:
        raise ValueError(f"Thiếu cột flood bắt buộc: {sorted(missing)}")
    if frame.empty:
        raise ValueError("Flood snapshot rỗng")
    key = ["river_point_id", "snapshot_at", "valid_date", "model"]
    if frame.duplicated(key).any():
        raise ValueError(f"Khóa flood bị trùng: {key}")

    rows = []
    for river_point_id, group in frame.groupby("river_point_id", sort=True):
        group = group.sort_values("valid_date").reset_index(drop=True)
        baseline = float(group.iloc[0]["river_discharge"])
        ending = float(group.iloc[-1]["river_discharge"])
        peak_index = group["river_discharge"].astype(float).idxmax()
        peak_row = group.loc[peak_index]
        peak = float(peak_row["river_discharge"])
        trend_signal, horizon_change_percent = _classify_trend(
            baseline,
            ending,
        )
        peak_change_percent = (
            None
            if baseline <= 0
            else (peak - baseline) / baseline * 100
        )
        median_peak = max(peak, 1e-9)
        uncertainty_ratio = (
            float(peak_row["river_discharge_p75"])
            - float(peak_row["river_discharge_p25"])
        ) / median_peak
        confidence = (
            "low"
            if uncertainty_ratio > 1
            else "medium"
            if uncertainty_ratio > 0.5
            else "high"
        )
        rows.append(
            {
                "river_point_id": river_point_id,
                "river_name": group.iloc[0]["river_name"],
                "point_name": group.iloc[0]["point_name"],
                "snapshot_at": group.iloc[0]["snapshot_at"],
                "baseline_discharge_m3s": baseline,
                "peak_discharge_m3s": peak,
                "peak_valid_date": peak_row["valid_date"],
                "peak_change_percent": peak_change_percent,
                "horizon_end_discharge_m3s": ending,
                "horizon_change_percent": horizon_change_percent,
                "ensemble_spread_ratio": uncertainty_ratio,
                "trend_signal": trend_signal,
                "confidence": confidence,
                "is_official_warning": False,
                "message_vi": (
                    "Tín hiệu mô phỏng GloFAS để theo dõi xu hướng; "
                    "không phải cảnh báo lũ chính thức."
                ),
                "model": group.iloc[0]["model"],
                "signal_version": SIGNAL_VERSION,
                "grid_latitude": float(group.iloc[0]["grid_latitude"]),
                "grid_longitude": float(group.iloc[0]["grid_longitude"]),
            }
        )
    result = pd.DataFrame(rows).sort_values("river_point_id").reset_index(
        drop=True
    )
    result["grid_cell_id"] = result.apply(
        lambda row: f"{row['grid_latitude']:.5f},{row['grid_longitude']:.5f}",
        axis=1,
    )
    result["grid_point_count"] = result.groupby("grid_cell_id")[
        "river_point_id"
    ].transform("size")
    result["is_representative_grid_cell"] = ~result.duplicated(
        "grid_cell_id"
    )
    return result


def atomic_write_parquet(frame: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    frame.to_parquet(temporary, index=False)
    os.replace(temporary, path)


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def generate_signals(flood_part_paths: list[Path], output: Path) -> pd.DataFrame:
    if not flood_part_paths:
        raise ValueError("Không tìm thấy flood part hoàn chỉnh")
    partition_paths = {path.resolve().parent for path in flood_part_paths}
    if len(partition_paths) != 1:
        raise ValueError("Các flood parts phải thuộc cùng một snapshot partition")
    source_manifest_path = flood_part_paths[0].parent / "_manifest.json"
    if not source_manifest_path.exists():
        raise ValueError("Flood snapshot thiếu _manifest.json")
    source_manifest = json.loads(
        source_manifest_path.read_text(encoding="utf-8")
    )
    if "river_points_sha256" not in source_manifest:
        raise ValueError("Flood manifest thiếu river_points_sha256")
    source_hashes = {
        str(path): file_sha256(path)
        for path in flood_part_paths
    }
    flood = pd.concat(
        [pd.read_parquet(path) for path in flood_part_paths],
        ignore_index=True,
    )
    signals = build_flood_signals(flood)
    manifest = {
        "signal_version": SIGNAL_VERSION,
        "rows": len(signals),
        "snapshot_at": str(signals["snapshot_at"].iloc[0]),
        "is_official_warning": False,
        "source_parts_sha256": source_hashes,
        "source_manifest": str(source_manifest_path),
        "source_manifest_sha256": file_sha256(source_manifest_path),
        "river_points_sha256": source_manifest["river_points_sha256"],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest_path = output.with_suffix(".manifest.json")
    temporary_output = output.with_suffix(output.suffix + ".tmp")
    temporary_manifest = manifest_path.with_suffix(".json.tmp")
    signals.to_parquet(temporary_output, index=False)
    temporary_manifest.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    os.replace(temporary_output, output)
    os.replace(temporary_manifest, manifest_path)
    return signals


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Tạo tín hiệu xu hướng lũ bổ trợ từ snapshot GloFAS."
    )
    parser.add_argument("--flood-parts", nargs="+", type=Path)
    parser.add_argument(
        "--flood-root",
        type=Path,
        default=Path("data/flood"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/flood_signals.parquet"),
    )
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    flood_parts = arguments.flood_parts
    if not flood_parts:
        flood_parts = sorted(
            latest_complete_partition(arguments.flood_root).glob(
                "part-*.parquet"
            )
        )
    result = generate_signals(flood_parts, arguments.output)
    print(f"Đã tạo {len(result)} tín hiệu GloFAS tại {arguments.output}")
