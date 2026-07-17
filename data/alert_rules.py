import argparse
import hashlib
import json
import sys
from pathlib import Path

import pandas as pd

try:
    from data.admin_units import OFFICIAL_NEW_ADMIN_UNITS
    from data.data_contract import TIMEZONE
    from data.download_forecast import file_sha256, validate_forecast_part
except ModuleNotFoundError:
    from admin_units import OFFICIAL_NEW_ADMIN_UNITS
    from data_contract import TIMEZONE
    from download_forecast import file_sha256, validate_forecast_part

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


RULE_VERSION = "mvp-1.0"
SEVERITY_RANK = {"warning": 1, "danger": 2}
ALERT_DTYPES = {
    "alert_id": "object",
    "location_id": "int64",
    "snapshot_at": f"datetime64[ns, {TIMEZONE}]",
    "valid_from": f"datetime64[ns, {TIMEZONE}]",
    "valid_to": f"datetime64[ns, {TIMEZONE}]",
    "hazard_type": "object",
    "severity": "object",
    "severity_rank": "int64",
    "confidence": "object",
    "metric_name": "object",
    "metric_value": "float64",
    "threshold_value": "float64",
    "threshold_unit": "object",
    "message_vi": "object",
    "recommended_action": "object",
    "source": "object",
    "model": "object",
    "rule_version": "object",
    "old_admin_unit": "object",
    "new_admin_unit": "object",
    "province": "object",
}


def empty_alert_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            name: pd.Series(dtype=dtype)
            for name, dtype in ALERT_DTYPES.items()
        }
    )


def confidence_for_lead(lead_hours: float) -> str:
    if lead_hours <= 72:
        return "high"
    if lead_hours <= 168:
        return "medium"
    return "low"


def make_alert_id(row: dict) -> str:
    raw = "|".join(
        str(row[name])
        for name in (
            "location_id",
            "snapshot_at",
            "valid_from",
            "hazard_type",
            "rule_version",
        )
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:20]


def build_alert(
    row: pd.Series,
    *,
    hazard_type: str,
    severity: str,
    metric_name: str,
    metric_value: float,
    threshold_value: float,
    threshold_unit: str,
    valid_from: pd.Timestamp,
    valid_to: pd.Timestamp,
    message_vi: str,
    recommended_action: str,
) -> dict:
    alert = {
        "location_id": int(row["location_id"]),
        "snapshot_at": row["snapshot_at"],
        "valid_from": valid_from,
        "valid_to": valid_to,
        "hazard_type": hazard_type,
        "severity": severity,
        "severity_rank": SEVERITY_RANK[severity],
        "confidence": confidence_for_lead(
            (valid_to - row["snapshot_at"]).total_seconds() / 3600
        ),
        "metric_name": metric_name,
        "metric_value": float(metric_value),
        "threshold_value": float(threshold_value),
        "threshold_unit": threshold_unit,
        "message_vi": message_vi,
        "recommended_action": recommended_action,
        "source": "Open-Meteo Forecast API",
        "model": row["model"],
        "rule_version": RULE_VERSION,
    }
    alert["alert_id"] = make_alert_id(alert)
    return alert


def rain_alerts(forecast: pd.DataFrame) -> list[dict]:
    alerts = []
    for _, group in forecast.groupby("location_id", sort=False):
        ordered = group.sort_values("valid_time").copy()
        ordered["rain_24h"] = ordered.rolling(
            "24h",
            on="valid_time",
            min_periods=24,
        )["precipitation"].sum()
        candidates = ordered[ordered["rain_24h"] > 50].copy()
        if candidates.empty:
            continue
        candidates["alert_date"] = candidates["valid_time"].dt.date
        daily_indices = candidates.groupby("alert_date")["rain_24h"].idxmax()
        for _, row in candidates.loc[daily_indices].iterrows():
            metric_value = float(row["rain_24h"])
            danger = metric_value > 100
            severity = "danger" if danger else "warning"
            threshold = 100.0 if danger else 50.0
            alerts.append(
                build_alert(
                    row,
                    hazard_type="heavy_rain",
                    severity=severity,
                    metric_name="rain_24h",
                    metric_value=metric_value,
                    threshold_value=threshold,
                    threshold_unit="mm/24h",
                    valid_from=row["valid_time"] - pd.Timedelta(hours=23),
                    valid_to=row["valid_time"],
                    message_vi=(
                        f"Dự báo mưa tích lũy 24 giờ khoảng "
                        f"{metric_value:.1f} mm."
                    ),
                    recommended_action=(
                        "Tránh qua suối, ngầm tràn; theo dõi thông báo của "
                        "chính quyền và chuẩn bị di chuyển khỏi nơi trũng thấp."
                    ),
                )
            )
    return alerts


def cold_alerts(forecast: pd.DataFrame) -> list[dict]:
    alerts = []
    working = forecast.copy()
    working["local_date"] = working["valid_time"].dt.date
    daily = (
        working.groupby(["location_id", "local_date"], as_index=False)
        .agg(
            snapshot_at=("snapshot_at", "first"),
            model=("model", "first"),
            valid_from=("valid_time", "min"),
            valid_to=("valid_time", "max"),
            daily_mean_temperature=("temperature_2m", "mean"),
            hourly_count=("valid_time", "nunique"),
        )
    )
    candidates = daily[
        (daily["hourly_count"] == 24)
        & (daily["daily_mean_temperature"] < 15)
    ]
    for _, row in candidates.iterrows():
        metric_value = float(row["daily_mean_temperature"])
        danger = metric_value < 13
        severity = "danger" if danger else "warning"
        threshold = 13.0 if danger else 15.0
        alerts.append(
            build_alert(
                row,
                hazard_type="cold",
                severity=severity,
                metric_name="daily_mean_temperature",
                metric_value=metric_value,
                threshold_value=threshold,
                threshold_unit="°C",
                valid_from=row["valid_from"],
                valid_to=row["valid_to"],
                message_vi=(
                    f"Nhiệt độ trung bình ngày dự báo "
                    f"{metric_value:.1f}°C."
                ),
                recommended_action=(
                    "Giữ ấm cho người, che chắn chuồng trại và bảo vệ "
                    "cây trồng, vật nuôi."
                ),
            )
        )
    return alerts


def prolonged_rain_alerts(forecast: pd.DataFrame) -> list[dict]:
    alerts = []
    working = forecast.copy()
    rain_72h_by_location_and_time = {}
    for location_id, group in working.groupby("location_id"):
        ordered = group.sort_values("valid_time")
        rolling_72h = ordered.rolling(
            "72h",
            on="valid_time",
            min_periods=72,
        )["precipitation"].sum()
        rain_72h_by_location_and_time.update(
            {
                (int(location_id), valid_time): value
                for valid_time, value in zip(
                    ordered["valid_time"],
                    rolling_72h,
                )
            }
        )
    working["local_date"] = working["valid_time"].dt.date
    daily = (
        working.groupby(["location_id", "local_date"], as_index=False)
        .agg(
            snapshot_at=("snapshot_at", "first"),
            model=("model", "first"),
            valid_from=("valid_time", "min"),
            valid_to=("valid_time", "max"),
            daily_rain=("precipitation", "sum"),
            hourly_count=("valid_time", "nunique"),
        )
        .sort_values(["location_id", "local_date"])
    )
    daily = daily[daily["hourly_count"] == 24].copy()
    daily["min_daily_rain_3d"] = daily.groupby("location_id")[
        "daily_rain"
    ].transform(lambda values: values.rolling(3, min_periods=3).min())
    daily["rain_72h"] = [
        rain_72h_by_location_and_time.get(
            (int(row.location_id), row.valid_to)
        )
        for row in daily.itertuples()
    ]
    candidates = daily[
        (daily["min_daily_rain_3d"] > 20)
        & (daily["rain_72h"] > 60)
    ]
    for _, row in candidates.iterrows():
        metric_value = float(row["rain_72h"])
        alerts.append(
            build_alert(
                row,
                hazard_type="prolonged_rain_signal",
                severity="warning",
                metric_name="rain_72h",
                metric_value=metric_value,
                threshold_value=60.0,
                threshold_unit="mm/72h, with each day >20mm",
                valid_from=row["valid_to"] - pd.Timedelta(hours=71),
                valid_to=row["valid_to"],
                message_vi=(
                    "Mưa kéo dài ba ngày; cần theo dõi nguy cơ lũ quét "
                    "và sạt lở tại khu vực nhạy cảm."
                ),
                recommended_action=(
                    "Theo dõi vết nứt, nước đục bất thường và thông báo "
                    "cho chính quyền; chưa coi đây là dự báo sạt lở chính thức."
                ),
            )
        )
    return alerts


def strong_wind_alerts(forecast: pd.DataFrame) -> list[dict]:
    alerts = []
    working = forecast.copy()
    working["local_date"] = working["valid_time"].dt.date
    daily_indices = working.groupby(
        ["location_id", "local_date"]
    )["wind_speed_10m"].idxmax()
    candidates = working.loc[daily_indices]
    candidates = candidates[candidates["wind_speed_10m"] > 60]
    for _, row in candidates.iterrows():
        metric_value = float(row["wind_speed_10m"])
        danger = metric_value > 90
        severity = "danger" if danger else "warning"
        threshold = 90.0 if danger else 60.0
        alerts.append(
            build_alert(
                row,
                hazard_type="strong_wind",
                severity=severity,
                metric_name="max_wind_speed_10m",
                metric_value=metric_value,
                threshold_value=threshold,
                threshold_unit="km/h sustained wind",
                valid_from=row["valid_time"],
                valid_to=row["valid_time"] + pd.Timedelta(hours=1),
                message_vi=(
                    f"Tốc độ gió duy trì ở độ cao 10 m dự báo đạt "
                    f"{metric_value:.1f} km/h."
                ),
                recommended_action=(
                    "Gia cố mái nhà và vật dụng ngoài trời; tránh đứng gần "
                    "cây lớn, biển quảng cáo và đường dây điện."
                ),
            )
        )
    return alerts


def wind_gust_alerts(forecast: pd.DataFrame) -> list[dict]:
    if (
        "wind_gusts_10m" not in forecast.columns
        or forecast["wind_gusts_10m"].isna().all()
    ):
        return []
    alerts = []
    working = forecast.dropna(subset=["wind_gusts_10m"]).copy()
    working["local_date"] = working["valid_time"].dt.date
    daily_indices = working.groupby(
        ["location_id", "local_date"]
    )["wind_gusts_10m"].idxmax()
    candidates = working.loc[daily_indices]
    candidates = candidates[candidates["wind_gusts_10m"] > 75]
    for _, row in candidates.iterrows():
        metric_value = float(row["wind_gusts_10m"])
        danger = metric_value > 100
        severity = "danger" if danger else "warning"
        threshold = 100.0 if danger else 75.0
        alerts.append(
            build_alert(
                row,
                hazard_type="strong_wind_gust",
                severity=severity,
                metric_name="max_wind_gusts_10m",
                metric_value=metric_value,
                threshold_value=threshold,
                threshold_unit="km/h gust",
                valid_from=row["valid_time"],
                valid_to=row["valid_time"] + pd.Timedelta(hours=1),
                message_vi=(
                    f"Gió giật ở độ cao 10 m dự báo đạt "
                    f"{metric_value:.1f} km/h theo rule sàng lọc MVP."
                ),
                recommended_action=(
                    "Gia cố mái nhà, đóng cửa và tránh đứng gần cây lớn "
                    "hoặc vật thể có thể bị gió cuốn."
                ),
            )
        )
    return alerts


def summarize_alerts(
    detail: pd.DataFrame,
    locations: pd.DataFrame,
) -> pd.DataFrame:
    if detail.empty:
        return detail.copy()
    enriched = detail.merge(
        locations[
            [
                "location_id",
                "old_admin_unit",
                "new_admin_unit",
                "province",
            ]
        ],
        on="location_id",
        how="left",
        validate="many_to_one",
    )
    enriched["valid_date"] = enriched["valid_to"].dt.date
    selected_indices = enriched.groupby(
        ["new_admin_unit", "hazard_type", "valid_date"],
        dropna=False,
    )["severity_rank"].idxmax()
    return (
        enriched.loc[selected_indices]
        .drop(columns=["valid_date"])
        .reset_index(drop=True)
    )


def build_new_admin_risk_overview(
    summary: pd.DataFrame,
    locations: pd.DataFrame,
) -> pd.DataFrame:
    covered_units = set(locations["new_admin_unit"].dropna().unique())
    units = pd.DataFrame(
        {
            "new_admin_unit": OFFICIAL_NEW_ADMIN_UNITS,
            "province": "Điện Biên",
        }
    )
    units["coverage_status"] = units["new_admin_unit"].map(
        lambda name: (
            "covered" if name in covered_units else "missing_location_data"
        )
    )
    if summary.empty:
        units["severity"] = "normal"
        units["severity_rank"] = 0
        units["hazard_type"] = "none"
        units["confidence"] = "none"
        units["valid_from"] = pd.NaT
        units["valid_to"] = pd.NaT
        units["alert_count"] = 0
        missing = units["coverage_status"] == "missing_location_data"
        units.loc[missing, "severity"] = "unavailable"
        units.loc[missing, "severity_rank"] = -1
        units.loc[missing, "hazard_type"] = "no_location_data"
        return units

    selected_indices = summary.groupby("new_admin_unit")[
        "severity_rank"
    ].idxmax()
    selected = summary.loc[
        selected_indices,
        [
            "new_admin_unit",
            "severity",
            "severity_rank",
            "hazard_type",
            "confidence",
            "valid_from",
            "valid_to",
        ],
    ]
    counts = (
        summary.groupby("new_admin_unit")
        .size()
        .rename("alert_count")
        .reset_index()
    )
    overview = units.merge(
        selected,
        on="new_admin_unit",
        how="left",
        validate="one_to_one",
    ).merge(
        counts,
        on="new_admin_unit",
        how="left",
        validate="one_to_one",
    )
    overview["severity"] = overview["severity"].fillna("normal")
    overview["severity_rank"] = (
        overview["severity_rank"].fillna(0).astype(int)
    )
    overview["hazard_type"] = overview["hazard_type"].fillna("none")
    overview["confidence"] = overview["confidence"].fillna("none")
    overview["alert_count"] = overview["alert_count"].fillna(0).astype(int)
    missing = overview["coverage_status"] == "missing_location_data"
    overview.loc[missing, "severity"] = "unavailable"
    overview.loc[missing, "severity_rank"] = -1
    overview.loc[missing, "hazard_type"] = "no_location_data"
    return overview


def generate_alerts(
    forecast: pd.DataFrame,
    locations: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    required = {
        "location_id",
        "snapshot_at",
        "valid_time",
        "model",
        "temperature_2m",
        "precipitation",
        "wind_speed_10m",
    }
    missing = required.difference(forecast.columns)
    if missing:
        raise ValueError(f"Forecast thiếu cột: {sorted(missing)}")
    alerts = [
        *rain_alerts(forecast),
        *cold_alerts(forecast),
        *prolonged_rain_alerts(forecast),
        *strong_wind_alerts(forecast),
        *wind_gust_alerts(forecast),
    ]
    detail = pd.DataFrame(alerts)
    if detail.empty:
        empty = empty_alert_frame()
        return empty, empty.copy()
    detail = detail.merge(
        locations[
            [
                "location_id",
                "old_admin_unit",
                "new_admin_unit",
                "province",
            ]
        ],
        on="location_id",
        how="left",
        validate="many_to_one",
    )
    summary = summarize_alerts(
        detail.drop(
            columns=[
                "old_admin_unit",
                "new_admin_unit",
                "province",
            ]
        ),
        locations,
    )
    return detail, summary


def validate_alert_output(frame: pd.DataFrame, *, summary: bool = False) -> None:
    required = {
        "alert_id",
        "location_id",
        "snapshot_at",
        "valid_from",
        "valid_to",
        "hazard_type",
        "severity",
        "confidence",
        "metric_name",
        "metric_value",
        "threshold_value",
        "threshold_unit",
        "message_vi",
        "recommended_action",
        "source",
        "model",
        "rule_version",
        "old_admin_unit",
        "new_admin_unit",
        "province",
    }
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"Alert output thiếu cột: {sorted(missing)}")
    if not summary and frame["alert_id"].duplicated().any():
        raise ValueError("Alert detail có alert_id trùng")
    for time_column in ("snapshot_at", "valid_from", "valid_to"):
        dtype = frame[time_column].dtype
        if not isinstance(dtype, pd.DatetimeTZDtype) or str(dtype.tz) != TIMEZONE:
            raise ValueError(
                f"{time_column} phải có timezone {TIMEZONE}, nhận {dtype}"
            )
    if frame[
        ["message_vi", "recommended_action", "metric_name"]
    ].isna().any().any():
        raise ValueError("Alert thiếu nội dung giải thích hoặc hành động")


def write_parquet_atomic(frame: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = path.with_suffix(".parquet.tmp")
    frame.to_parquet(
        temporary_path,
        index=False,
        engine="pyarrow",
        compression="zstd",
    )
    temporary_path.replace(path)


def hash_forecast_partition(partition: Path) -> str:
    digest = hashlib.sha256()
    source_paths = [
        partition / "_manifest.json",
        *sorted(partition.glob("part-*.parquet")),
    ]
    for path in source_paths:
        digest.update(path.name.encode("utf-8"))
        with path.open("rb") as source:
            for chunk in iter(lambda: source.read(1024 * 1024), b""):
                digest.update(chunk)
    return digest.hexdigest()


def latest_forecast_partition(forecast_root: Path) -> Path:
    success_markers = sorted(
        forecast_root.glob(
            "snapshot_date=*/snapshot_time=*/_SUCCESS"
        )
    )
    if not success_markers:
        raise ValueError(
            f"Không tìm thấy forecast snapshot hoàn chỉnh trong {forecast_root}"
        )
    return success_markers[-1].parent


def load_forecast_partition(
    partition: Path,
    locations: pd.DataFrame,
    locations_sha256: str,
) -> pd.DataFrame:
    if not (partition / "_SUCCESS").exists():
        raise ValueError(f"Snapshot chưa hoàn chỉnh: {partition}")
    manifest = json.loads(
        (partition / "_manifest.json").read_text(encoding="utf-8")
    )
    if manifest.get("locations_sha256") != locations_sha256:
        raise ValueError("Forecast snapshot không khớp locations hiện tại")
    batch_size = int(manifest["batch_size"])
    expected_hours = int(manifest["forecast_hours"])
    expected_parts = (len(locations) + batch_size - 1) // batch_size
    parts = sorted(partition.glob("part-*.parquet"))
    if len(parts) != expected_parts:
        raise ValueError(
            f"Snapshot có {len(parts)} part, cần {expected_parts}: {partition}"
        )
    frames = []
    for part_index, path in enumerate(parts):
        frame = pd.read_parquet(path)
        batch = locations.iloc[
            part_index * batch_size : (part_index + 1) * batch_size
        ]
        validate_forecast_part(
            frame,
            set(batch["location_id"].astype(int)),
            expected_hours,
        )
        frames.append(frame)
    return pd.concat(frames, ignore_index=True)


def run_alert_pipeline(
    forecast_partition: Path,
    locations_path: Path,
    output_root: Path,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, Path]:
    locations = pd.read_parquet(locations_path).sort_values("location_id")
    forecast = load_forecast_partition(
        forecast_partition,
        locations,
        file_sha256(locations_path),
    )
    detail, summary = generate_alerts(forecast, locations)
    validate_alert_output(detail)
    validate_alert_output(summary, summary=True)
    overview = build_new_admin_risk_overview(summary, locations)

    manifest = json.loads(
        (forecast_partition / "_manifest.json").read_text(encoding="utf-8")
    )
    snapshot_at = pd.Timestamp(manifest["snapshot_at"])
    output_dir = (
        output_root
        / f"snapshot_date={snapshot_at:%Y-%m-%d}"
        / f"snapshot_time={snapshot_at:%H%M}"
    )
    detail_path = output_dir / "alert_detail.parquet"
    summary_path = output_dir / "new_admin_summary.parquet"
    overview_path = output_dir / "new_admin_risk_overview.parquet"
    write_parquet_atomic(detail, detail_path)
    write_parquet_atomic(summary, summary_path)
    write_parquet_atomic(overview, overview_path)
    output_manifest = {
        "dataset": "dien_bien_weather_alerts",
        "source_forecast": str(forecast_partition),
        "source_forecast_sha256": hash_forecast_partition(
            forecast_partition
        ),
        "snapshot_at": snapshot_at.isoformat(),
        "timezone": TIMEZONE,
        "rule_version": RULE_VERSION,
        "detail_alerts": len(detail),
        "summary_alerts": len(summary),
        "old_locations_alerted": int(detail["location_id"].nunique()),
        "new_admin_units_alerted": int(
            summary["new_admin_unit"].nunique()
        ),
        "new_admin_units_total": int(
            overview["new_admin_unit"].nunique()
        ),
    }
    manifest_path = output_dir / "_manifest.json"
    temporary_manifest = manifest_path.with_suffix(".json.tmp")
    temporary_manifest.write_text(
        json.dumps(output_manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    temporary_manifest.replace(manifest_path)
    return detail, summary, overview, output_dir


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Sinh cảnh báo MVP từ forecast snapshot Điện Biên."
    )
    parser.add_argument(
        "--forecast-root",
        type=Path,
        default=Path("data/forecast"),
    )
    parser.add_argument("--forecast-partition", type=Path)
    parser.add_argument(
        "--locations",
        type=Path,
        default=Path("data/dien_bien_locations.parquet"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/alerts"),
    )
    args = parser.parse_args()

    partition = (
        args.forecast_partition
        if args.forecast_partition is not None
        else latest_forecast_partition(args.forecast_root)
    )
    detail, summary, overview, output_dir = run_alert_pipeline(
        partition,
        args.locations,
        args.output,
    )
    print(
        f"Đã sinh {len(detail)} cảnh báo chi tiết và "
        f"{len(summary)} cảnh báo cấp đơn vị mới; "
        f"overview đủ {len(overview)} đơn vị -> {output_dir}"
    )


if __name__ == "__main__":
    main()
