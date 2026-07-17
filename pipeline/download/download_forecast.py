import argparse
import hashlib
import json
import math
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from pipeline.shared.data_contract import (
    FORECAST_OPTIONAL_VARIABLES,
    FORECAST_REQUIRED_VARIABLES,
    TIMEZONE,
    validate_forecast_output,
)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
MODEL = "open_meteo_best_match"
HOURLY_VARIABLES = [
    "temperature_2m",
    "relative_humidity_2m",
    "precipitation",
    "precipitation_probability",
    "weather_code",
    "wind_speed_10m",
    "wind_gusts_10m",
]


def create_session() -> requests.Session:
    retry = Retry(
        total=5,
        backoff_factor=5,
        backoff_max=60,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET",),
        respect_retry_after_header=True,
    )
    session = requests.Session()
    session.mount("https://", HTTPAdapter(max_retries=retry))
    return session


def batched(frame: pd.DataFrame, batch_size: int):
    for start in range(0, len(frame), batch_size):
        yield start // batch_size, frame.iloc[start : start + batch_size]


def normalize_snapshot_at(value: str | None = None) -> pd.Timestamp:
    timestamp = (
        pd.Timestamp.now(tz=TIMEZONE)
        if value is None
        else pd.Timestamp(value)
    )
    if timestamp.tzinfo is None:
        timestamp = timestamp.tz_localize(TIMEZONE)
    else:
        timestamp = timestamp.tz_convert(TIMEZONE)
    return timestamp.floor("h")


def fetch_batch(
    session: requests.Session,
    locations: pd.DataFrame,
    forecast_hours: int,
) -> list[dict]:
    response = session.get(
        FORECAST_URL,
        params={
            "latitude": ",".join(locations["latitude"].astype(str)),
            "longitude": ",".join(locations["longitude"].astype(str)),
            "hourly": ",".join(HOURLY_VARIABLES),
            "forecast_hours": forecast_hours,
            "timezone": TIMEZONE,
        },
        timeout=120,
    )
    response.raise_for_status()
    payload = response.json()
    return payload if isinstance(payload, list) else [payload]


def parse_api_times(values: list[str]) -> pd.Series:
    times = pd.Series(pd.to_datetime(values))
    if times.dt.tz is None:
        return times.dt.tz_localize(
            TIMEZONE,
            ambiguous="raise",
            nonexistent="raise",
        )
    return times.dt.tz_convert(TIMEZONE)


def responses_to_frame(
    locations: pd.DataFrame,
    responses: list[dict],
    snapshot_at: pd.Timestamp,
    retrieved_at: pd.Timestamp,
) -> tuple[pd.DataFrame, list[str]]:
    if len(responses) != len(locations):
        raise ValueError(
            f"API trả {len(responses)} vị trí cho {len(locations)} yêu cầu"
        )

    frames = []
    for location, response in zip(
        locations.to_dict(orient="records"),
        responses,
    ):
        hourly = response.get("hourly", {})
        missing_required = set(FORECAST_REQUIRED_VARIABLES).difference(hourly)
        if missing_required:
            raise ValueError(
                f"API thiếu biến bắt buộc: {sorted(missing_required)}"
            )
        frame = pd.DataFrame(hourly)
        for variable in FORECAST_OPTIONAL_VARIABLES:
            if variable not in frame:
                frame[variable] = None
        frame = frame.rename(columns={"time": "valid_time"})
        frame["valid_time"] = parse_api_times(
            frame["valid_time"].tolist()
        ).array
        frame.insert(0, "location_id", int(location["location_id"]))
        frame["snapshot_at"] = snapshot_at
        frame["model"] = MODEL
        frame["lead_hours"] = (
            frame["valid_time"] - snapshot_at
        ).dt.total_seconds() / 3600
        frame["requested_latitude"] = float(location["latitude"])
        frame["requested_longitude"] = float(location["longitude"])
        frame["grid_latitude"] = float(response["latitude"])
        frame["grid_longitude"] = float(response["longitude"])
        frame["grid_elevation"] = float(response["elevation"])
        frame["timezone"] = response.get("timezone", TIMEZONE)
        frame["retrieved_at"] = retrieved_at
        frames.append(frame)

    combined = pd.concat(frames, ignore_index=True)
    warnings = validate_forecast_output(
        combined,
        set(locations["location_id"].astype(int)),
    )
    validate_grid_distance(combined)
    return combined, warnings


def validate_grid_distance(
    frame: pd.DataFrame,
    max_distance_km: float = 50.0,
) -> None:
    latitude_1 = np.radians(frame["requested_latitude"].astype(float))
    longitude_1 = np.radians(frame["requested_longitude"].astype(float))
    latitude_2 = np.radians(frame["grid_latitude"].astype(float))
    longitude_2 = np.radians(frame["grid_longitude"].astype(float))
    latitude_delta = latitude_2 - latitude_1
    longitude_delta = longitude_2 - longitude_1
    haversine = (
        np.sin(latitude_delta / 2) ** 2
        + np.cos(latitude_1)
        * np.cos(latitude_2)
        * np.sin(longitude_delta / 2) ** 2
    )
    distance_km = 6_371.0 * 2 * np.arcsin(np.sqrt(haversine))
    if (distance_km > max_distance_km).any():
        raise ValueError(
            f"Grid forecast lệch quá {max_distance_km:g} km so với input"
        )


def validate_forecast_part(
    frame: pd.DataFrame,
    expected_location_ids: set[int],
    expected_hours: int,
) -> list[str]:
    warnings = validate_forecast_output(frame, expected_location_ids)
    validate_grid_distance(frame)
    counts = frame.groupby("location_id")["valid_time"].nunique()
    if not (counts == expected_hours).all():
        raise ValueError(
            f"Số mốc forecast không khớp {expected_hours}: {counts.to_dict()}"
        )
    for location_id, group in frame.groupby("location_id"):
        times = group["valid_time"].sort_values()
        if len(times) > 1 and not (
            times.diff().dropna() == pd.Timedelta(hours=1)
        ).all():
            raise ValueError(
                f"valid_time của location_id {int(location_id)} "
                "không liên tục 1 giờ"
            )
        if (group["lead_hours"] < 0).any():
            raise ValueError(
                f"location_id {int(location_id)} có lead_hours âm"
            )
    return warnings


def write_forecast_part(
    frame: pd.DataFrame,
    output_path: Path,
    expected_location_ids: set[int],
    expected_hours: int,
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
    validate_forecast_part(
        written,
        expected_location_ids,
        expected_hours,
    )
    temporary_path.replace(output_path)


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def snapshot_directory(
    output_dir: Path,
    snapshot_at: pd.Timestamp,
) -> Path:
    return (
        output_dir
        / f"snapshot_date={snapshot_at:%Y-%m-%d}"
        / f"snapshot_time={snapshot_at:%H%M}"
    )


def ensure_manifest(
    partition_dir: Path,
    locations_path: Path,
    snapshot_at: pd.Timestamp,
    batch_size: int,
    forecast_hours: int,
) -> None:
    manifest = {
        "dataset": "dien_bien_hourly_forecast_snapshot",
        "source": "Open-Meteo Forecast API",
        "model": MODEL,
        "timezone": TIMEZONE,
        "snapshot_at": snapshot_at.isoformat(),
        "forecast_hours": forecast_hours,
        "batch_size": batch_size,
        "hourly_variables": HOURLY_VARIABLES,
        "locations_sha256": file_sha256(locations_path),
        "partitioning": ["snapshot_date", "snapshot_time"],
    }
    partition_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = partition_dir / "_manifest.json"
    if manifest_path.exists():
        existing = json.loads(manifest_path.read_text(encoding="utf-8"))
        if existing != manifest:
            raise ValueError("Manifest snapshot hiện tại không tương thích")
        return
    temporary_path = manifest_path.with_suffix(".json.tmp")
    temporary_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    temporary_path.replace(manifest_path)


def download_forecast(
    locations_path: Path,
    output_dir: Path,
    snapshot_at: pd.Timestamp,
    batch_size: int = 15,
    forecast_hours: int = 384,
    request_delay: float = 5.0,
) -> tuple[Path, int, int]:
    locations = pd.read_parquet(locations_path).sort_values("location_id")
    if batch_size <= 0:
        raise ValueError("batch_size phải lớn hơn 0")
    if forecast_hours <= 0:
        raise ValueError("forecast_hours phải lớn hơn 0")
    partition_dir = snapshot_directory(output_dir, snapshot_at)
    ensure_manifest(
        partition_dir,
        locations_path,
        snapshot_at,
        batch_size,
        forecast_hours,
    )

    session = create_session()
    downloaded_parts = 0
    skipped_parts = 0
    batch_count = math.ceil(len(locations) / batch_size)
    for batch_index, location_batch in batched(locations, batch_size):
        output_path = partition_dir / f"part-{batch_index:03d}.parquet"
        expected_ids = set(location_batch["location_id"].astype(int))
        if output_path.exists():
            try:
                existing = pd.read_parquet(output_path)
                validate_forecast_part(
                    existing,
                    expected_ids,
                    forecast_hours,
                )
                skipped_parts += 1
                print(
                    f"[{batch_index + 1}/{batch_count}] "
                    f"bỏ qua part đã xác thực"
                )
                continue
            except (OSError, ValueError):
                output_path.unlink(missing_ok=True)

        responses = fetch_batch(
            session,
            location_batch,
            forecast_hours,
        )
        retrieved_at = pd.Timestamp.now(tz=TIMEZONE)
        frame, warnings = responses_to_frame(
            location_batch,
            responses,
            snapshot_at,
            retrieved_at,
        )
        write_forecast_part(
            frame,
            output_path,
            expected_ids,
            forecast_hours,
        )
        for warning in warnings:
            print(f"WARNING batch {batch_index + 1}: {warning}")
        downloaded_parts += 1
        print(
            f"[{batch_index + 1}/{batch_count}] "
            f"{len(frame):,} dòng -> {output_path}"
        )
        if batch_index + 1 < batch_count:
            time.sleep(request_delay)

    success_path = partition_dir / "_SUCCESS"
    temporary_success = success_path.with_suffix(".tmp")
    temporary_success.write_text(
        json.dumps(
            {
                "snapshot_at": snapshot_at.isoformat(),
                "completed_at": pd.Timestamp.now(tz=TIMEZONE).isoformat(),
                "parts": batch_count,
                "locations": len(locations),
                "rows": len(locations) * forecast_hours,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    temporary_success.replace(success_path)
    return partition_dir, downloaded_parts, skipped_parts


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Tải Open-Meteo forecast dạng snapshot cho Điện Biên."
    )
    parser.add_argument(
        "--locations",
        type=Path,
        default=Path("data/reference/dien_bien_locations.parquet"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/weather/forecast"),
    )
    parser.add_argument("--snapshot-at")
    parser.add_argument("--batch-size", type=int, default=15)
    parser.add_argument("--forecast-hours", type=int, default=384)
    parser.add_argument("--request-delay", type=float, default=5.0)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    locations = pd.read_parquet(args.locations)
    snapshot_at = normalize_snapshot_at(args.snapshot_at)
    parts = math.ceil(len(locations) / args.batch_size)
    rows = len(locations) * args.forecast_hours
    print(
        f"Snapshot {snapshot_at.isoformat()} | {len(locations)} địa điểm | "
        f"{parts} part | {rows:,} dòng"
    )
    if args.dry_run:
        return

    partition_dir, downloaded, skipped = download_forecast(
        args.locations,
        args.output,
        snapshot_at,
        args.batch_size,
        args.forecast_hours,
        args.request_delay,
    )
    print(
        f"Snapshot hoàn tất: tải {downloaded} part, "
        f"bỏ qua {skipped} part -> {partition_dir}"
    )


if __name__ == "__main__":
    main()
