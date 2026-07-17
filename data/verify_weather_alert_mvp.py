import argparse
import json
import math
import sys
from pathlib import Path

import pandas as pd

try:
    from data.admin_units import OFFICIAL_NEW_ADMIN_UNITS
    from data.alert_rules import (
        RULE_VERSION,
        build_new_admin_risk_overview,
        generate_alerts,
        hash_forecast_partition,
        latest_forecast_partition,
        validate_alert_output,
    )
    from data.data_contract import validate_forecast_output
    from data.download_elevation import validate_location_features
    from data.download_forecast import file_sha256, validate_forecast_part
except ModuleNotFoundError:
    from admin_units import OFFICIAL_NEW_ADMIN_UNITS
    from alert_rules import (
        RULE_VERSION,
        build_new_admin_risk_overview,
        generate_alerts,
        hash_forecast_partition,
        latest_forecast_partition,
        validate_alert_output,
    )
    from data_contract import validate_forecast_output
    from download_elevation import validate_location_features
    from download_forecast import file_sha256, validate_forecast_part

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def verify_mvp(
    locations_path: Path,
    features_path: Path,
    forecast_partition: Path,
    alerts_partition: Path,
) -> dict:
    locations = pd.read_parquet(locations_path).sort_values("location_id")
    expected_ids = set(locations["location_id"].astype(int))
    locations_sha256 = file_sha256(locations_path)

    features = pd.read_parquet(features_path)
    validate_location_features(features, expected_ids)
    features_manifest = json.loads(
        features_path.with_suffix(".manifest.json").read_text(
            encoding="utf-8"
        )
    )
    if features_manifest.get("locations_sha256") != locations_sha256:
        raise ValueError("Location features không khớp locations hiện tại")

    forecast_manifest = json.loads(
        (forecast_partition / "_manifest.json").read_text(encoding="utf-8")
    )
    expected_hours = int(forecast_manifest["forecast_hours"])
    if forecast_manifest.get("locations_sha256") != locations_sha256:
        raise ValueError("Forecast không khớp locations hiện tại")
    batch_size = int(forecast_manifest["batch_size"])
    expected_parts = math.ceil(len(locations) / batch_size)
    part_paths = sorted(forecast_partition.glob("part-*.parquet"))
    if len(part_paths) != expected_parts:
        raise ValueError(
            f"Forecast có {len(part_paths)} part, cần {expected_parts}"
        )

    forecast_parts = []
    for part_index, path in enumerate(part_paths):
        part = pd.read_parquet(path)
        start = part_index * batch_size
        batch = locations.iloc[start : start + batch_size]
        validate_forecast_part(
            part,
            set(batch["location_id"].astype(int)),
            expected_hours,
        )
        forecast_parts.append(part)
    forecast = pd.concat(forecast_parts, ignore_index=True)
    warnings = validate_forecast_output(forecast, expected_ids)

    detail = pd.read_parquet(alerts_partition / "alert_detail.parquet")
    summary = pd.read_parquet(
        alerts_partition / "new_admin_summary.parquet"
    )
    overview = pd.read_parquet(
        alerts_partition / "new_admin_risk_overview.parquet"
    )
    validate_alert_output(detail)
    validate_alert_output(summary, summary=True)
    alert_manifest = json.loads(
        (alerts_partition / "_manifest.json").read_text(encoding="utf-8")
    )
    if alert_manifest["snapshot_at"] != forecast_manifest["snapshot_at"]:
        raise ValueError("Alert manifest không khớp snapshot_at của forecast")
    if alert_manifest["rule_version"] != RULE_VERSION:
        raise ValueError("Alert manifest không khớp rule version hiện tại")
    if alert_manifest["detail_alerts"] != len(detail):
        raise ValueError("Số alert detail không khớp manifest")
    if alert_manifest["summary_alerts"] != len(summary):
        raise ValueError("Số alert summary không khớp manifest")
    for frame_name, frame in (("detail", detail), ("summary", summary)):
        if not frame.empty and set(frame["rule_version"]) != {RULE_VERSION}:
            raise ValueError(
                f"Alert {frame_name} có row dùng rule version khác"
            )
    expected_forecast_hash = hash_forecast_partition(forecast_partition)
    if (
        alert_manifest.get("source_forecast_sha256")
        != expected_forecast_hash
    ):
        raise ValueError("Alert không được sinh từ forecast snapshot hiện tại")
    for frame_name, frame in (("detail", detail), ("summary", summary)):
        if not frame.empty and set(
            frame["snapshot_at"].map(pd.Timestamp).map(str)
        ) != {str(pd.Timestamp(forecast_manifest["snapshot_at"]))}:
            raise ValueError(
                f"Alert {frame_name} có snapshot_at không khớp forecast"
            )
    expected_new_units = len(OFFICIAL_NEW_ADMIN_UNITS)
    if overview["new_admin_unit"].nunique() != expected_new_units:
        raise ValueError(
            f"Overview có {overview['new_admin_unit'].nunique()} đơn vị mới, "
            f"cần {expected_new_units}"
        )
    if overview["new_admin_unit"].duplicated().any():
        raise ValueError("Overview có đơn vị mới trùng")
    if set(overview["new_admin_unit"]) != set(OFFICIAL_NEW_ADMIN_UNITS):
        raise ValueError("Overview không khớp danh mục 45 đơn vị chính thức")
    covered_names = set(locations["new_admin_unit"].dropna().unique())
    covered = overview["new_admin_unit"].isin(covered_names)
    if not (overview.loc[covered, "coverage_status"] == "covered").all():
        raise ValueError("Overview đánh dấu sai đơn vị đã có location")
    missing = ~covered
    if not (
        (
            overview.loc[missing, "coverage_status"]
            == "missing_location_data"
        )
        & (overview.loc[missing, "severity"] == "unavailable")
    ).all():
        raise ValueError("Overview không đánh dấu unavailable cho đơn vị thiếu")
    if not set(detail["location_id"]).issubset(expected_ids):
        raise ValueError("Alert chứa location_id ngoài locations master")

    expected_detail, expected_summary = generate_alerts(
        forecast,
        locations,
    )
    expected_overview = build_new_admin_risk_overview(
        expected_summary,
        locations,
    )
    comparisons = [
        ("detail", detail, expected_detail, ["alert_id"]),
        (
            "summary",
            summary,
            expected_summary,
            ["new_admin_unit", "hazard_type", "valid_to"],
        ),
        (
            "overview",
            overview,
            expected_overview,
            ["new_admin_unit"],
        ),
    ]
    for name, actual, expected, sort_columns in comparisons:
        actual_sorted = actual.sort_values(sort_columns).reset_index(drop=True)
        expected_sorted = expected.sort_values(sort_columns).reset_index(
            drop=True
        )
        try:
            pd.testing.assert_frame_equal(
                actual_sorted[expected_sorted.columns],
                expected_sorted,
                check_dtype=False,
                check_exact=False,
                rtol=1e-10,
                atol=1e-10,
            )
        except AssertionError as error:
            raise ValueError(
                f"Alert {name} không khớp kết quả tái tính từ forecast"
            ) from error

    return {
        "locations": len(locations),
        "covered_new_admin_units": expected_new_units,
        "new_admin_units_with_locations": int(
            locations["new_admin_unit"].nunique()
        ),
        "location_features": len(features),
        "forecast_parts": len(part_paths),
        "forecast_rows": len(forecast),
        "forecast_hours": expected_hours,
        "forecast_warnings": warnings,
        "detail_alerts": len(detail),
        "summary_alerts": len(summary),
        "overview_rows": len(overview),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--locations",
        type=Path,
        default=Path("data/dien_bien_locations.parquet"),
    )
    parser.add_argument(
        "--features",
        type=Path,
        default=Path("data/location_features.parquet"),
    )
    parser.add_argument(
        "--forecast-root",
        type=Path,
        default=Path("data/forecast"),
    )
    parser.add_argument("--forecast-partition", type=Path)
    parser.add_argument(
        "--alerts-root",
        type=Path,
        default=Path("data/alerts"),
    )
    parser.add_argument("--alerts-partition", type=Path)
    args = parser.parse_args()

    forecast_partition = (
        args.forecast_partition
        if args.forecast_partition is not None
        else latest_forecast_partition(args.forecast_root)
    )
    alerts_partition = (
        args.alerts_partition
        if args.alerts_partition is not None
        else args.alerts_root
        / forecast_partition.parent.name
        / forecast_partition.name
    )
    result = verify_mvp(
        args.locations,
        args.features,
        forecast_partition,
        alerts_partition,
    )
    print(
        "VERIFY PASS: "
        f"{result['locations']} điểm cũ → "
        f"{result['new_admin_units_with_locations']}/"
        f"{result['covered_new_admin_units']} đơn vị mới có location | "
        f"{result['forecast_rows']:,} forecast rows | "
        f"{result['forecast_parts']} part | "
        f"{result['detail_alerts']} alert detail | "
        f"{result['overview_rows']} overview rows"
    )


if __name__ == "__main__":
    main()
