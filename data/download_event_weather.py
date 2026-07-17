import argparse
import hashlib
import json
import math
import re
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
TIMEZONE = "Asia/Ho_Chi_Minh"
MODEL = "era5"
HOURLY_VARIABLES = [
    "temperature_2m",
    "relative_humidity_2m",
    "precipitation",
    "rain",
    "weather_code",
    "wind_speed_10m",
    "soil_moisture_0_to_7cm",
]
EVENT_REQUIRED_COLUMNS = {
    "event_id",
    "event_date",
    "spatial_precision",
    "source_name",
    "source_record_id",
    "source_url",
}
LOCATION_REQUIRED_COLUMNS = {"location_id", "latitude", "longitude"}
EVENT_ID_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}")


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    temporary.replace(path)


def create_session() -> requests.Session:
    retry = Retry(
        total=6,
        backoff_factor=10,
        backoff_max=120,
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


def local_midnight(value: object) -> pd.Timestamp:
    timestamp = pd.Timestamp(value)
    if timestamp.tzinfo is None:
        timestamp = timestamp.tz_localize(TIMEZONE)
    else:
        timestamp = timestamp.tz_convert(TIMEZONE)
    return timestamp.normalize()


def event_window(
    event_date: object,
    pre_hours: int = 72,
    post_hours: int = 48,
) -> tuple[pd.Timestamp, pd.Timestamp, pd.Timestamp]:
    event_at = local_midnight(event_date)
    return (
        event_at - pd.Timedelta(hours=pre_hours),
        event_at,
        event_at + pd.Timedelta(hours=post_hours),
    )


def fetch_batch(
    session: requests.Session,
    locations: pd.DataFrame,
    start_date: str,
    end_date: str,
) -> list[dict]:
    response = session.get(
        ARCHIVE_URL,
        params={
            "latitude": ",".join(locations["latitude"].astype(str)),
            "longitude": ",".join(locations["longitude"].astype(str)),
            "start_date": start_date,
            "end_date": end_date,
            "hourly": ",".join(HOURLY_VARIABLES),
            "timezone": TIMEZONE,
            "models": MODEL,
        },
        timeout=180,
    )
    response.raise_for_status()
    payload = response.json()
    return payload if isinstance(payload, list) else [payload]


def parse_times(values: list[str]) -> pd.Series:
    times = pd.Series(pd.to_datetime(values))
    if times.dt.tz is None:
        return times.dt.tz_localize(TIMEZONE, ambiguous="raise", nonexistent="raise")
    return times.dt.tz_convert(TIMEZONE)


def grid_distance_km(frame: pd.DataFrame) -> pd.Series:
    lat1 = np.radians(frame["requested_latitude"].astype(float))
    lon1 = np.radians(frame["requested_longitude"].astype(float))
    lat2 = np.radians(frame["grid_latitude"].astype(float))
    lon2 = np.radians(frame["grid_longitude"].astype(float))
    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1
    value = (
        np.sin(delta_lat / 2) ** 2
        + np.cos(lat1) * np.cos(lat2) * np.sin(delta_lon / 2) ** 2
    )
    return pd.Series(6371.0 * 2 * np.arcsin(np.sqrt(value)), index=frame.index)


def responses_to_frame(
    event: dict,
    locations: pd.DataFrame,
    responses: list[dict],
    window_start: pd.Timestamp,
    event_at: pd.Timestamp,
    window_end: pd.Timestamp,
    retrieved_at: pd.Timestamp,
) -> pd.DataFrame:
    if len(responses) != len(locations):
        raise ValueError(
            f"API trả {len(responses)} vị trí cho {len(locations)} vị trí yêu cầu"
        )
    frames = []
    for location, response in zip(locations.to_dict("records"), responses):
        hourly = response.get("hourly", {})
        missing = {"time", *HOURLY_VARIABLES}.difference(hourly)
        if missing:
            raise ValueError(f"API thiếu biến hourly: {sorted(missing)}")
        frame = pd.DataFrame(hourly)
        frame["time"] = parse_times(frame["time"].tolist()).array
        frame = frame[
            frame["time"].between(window_start, window_end, inclusive="both")
        ].copy()
        frame.insert(0, "event_id", str(event["event_id"]))
        frame.insert(1, "location_id", int(location["location_id"]))
        frame["event_at"] = event_at
        frame["window_start"] = window_start
        frame["window_end"] = window_end
        frame["training_feature_eligible"] = frame["time"] < event_at
        frame["spatial_precision"] = str(event["spatial_precision"])
        frame["model"] = MODEL
        frame["requested_latitude"] = float(location["latitude"])
        frame["requested_longitude"] = float(location["longitude"])
        frame["grid_latitude"] = float(response["latitude"])
        frame["grid_longitude"] = float(response["longitude"])
        frame["grid_elevation"] = float(response["elevation"])
        frame["timezone"] = response.get("timezone", TIMEZONE)
        frame["retrieved_at"] = retrieved_at
        frames.append(frame)
    combined = pd.concat(frames, ignore_index=True)
    validate_event_part(
        combined,
        str(event["event_id"]),
        locations,
        window_start,
        event_at,
        window_end,
        str(event["spatial_precision"]),
    )
    return combined


def validate_event_part(
    frame: pd.DataFrame,
    event_id: str,
    expected_locations: pd.DataFrame,
    window_start: pd.Timestamp,
    event_at: pd.Timestamp,
    window_end: pd.Timestamp,
    spatial_precision: str,
    max_grid_distance_km: float = 50.0,
) -> None:
    expected_location_ids = set(expected_locations["location_id"].astype(int))
    required = {
        "event_id", "location_id", "time", "event_at", "window_start",
        "window_end", "training_feature_eligible", "spatial_precision",
        "model", "requested_latitude", "requested_longitude", "grid_latitude",
        "grid_longitude", "grid_elevation", "timezone", "retrieved_at",
        *HOURLY_VARIABLES,
    }
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"Part thiếu cột: {sorted(missing)}")
    if frame.empty:
        raise ValueError("Part không có bản ghi")
    if set(frame["event_id"].astype(str)) != {event_id}:
        raise ValueError("event_id trong part không khớp")
    if set(frame["model"].astype(str)) != {MODEL}:
        raise ValueError("model trong part không khớp")
    if set(frame["spatial_precision"].astype(str)) != {spatial_precision}:
        raise ValueError("spatial_precision trong part không khớp")
    if frame["event_at"].nunique() != 1 or frame["event_at"].iloc[0] != event_at:
        raise ValueError("event_at trong part không khớp")
    if frame["window_start"].nunique() != 1 or frame["window_start"].iloc[0] != window_start:
        raise ValueError("window_start trong part không khớp")
    if frame["window_end"].nunique() != 1 or frame["window_end"].iloc[0] != window_end:
        raise ValueError("window_end trong part không khớp")
    if set(frame["location_id"].astype(int)) != expected_location_ids:
        raise ValueError("location_id trong part không đủ coverage")
    expected_by_id = expected_locations.set_index("location_id")
    if frame.duplicated(["event_id", "location_id", "time", "model"]).any():
        raise ValueError("Part có khóa sự kiện/thời gian trùng")
    expected_hours = int((window_end - window_start).total_seconds() / 3600) + 1
    for location_id, group in frame.groupby("location_id"):
        expected = expected_by_id.loc[int(location_id)]
        for column, master_column in [
            ("requested_latitude", "latitude"),
            ("requested_longitude", "longitude"),
        ]:
            values = group[column].astype(float)
            if values.nunique(dropna=False) != 1 or not np.isclose(
                values.to_numpy(),
                float(expected[master_column]),
                rtol=0,
                atol=1e-9,
            ).all():
                raise ValueError(
                    f"location_id {int(location_id)} không khớp location master"
                )
        times = group["time"].sort_values()
        if len(times) != expected_hours or times.nunique() != expected_hours:
            raise ValueError(
                f"location_id {int(location_id)} cần đúng {expected_hours} giờ"
            )
        if times.iloc[0] != window_start or times.iloc[-1] != window_end:
            raise ValueError("Part không phủ đúng biên cửa sổ")
        if not (times.diff().dropna() == pd.Timedelta(hours=1)).all():
            raise ValueError("Cadence trong part không liên tục 1 giờ")
        null_counts = {
            name: int(group[name].isna().sum())
            for name in HOURLY_VARIABLES
            if group[name].isna().any()
        }
        if null_counts:
            raise ValueError(
                f"location_id {int(location_id)} có giá trị thời tiết rỗng: "
                f"{null_counts}"
            )
    for column in ("time", "event_at", "window_start", "window_end", "retrieved_at"):
        dtype = frame[column].dtype
        if not isinstance(dtype, pd.DatetimeTZDtype) or str(dtype.tz) != TIMEZONE:
            raise ValueError(f"{column} phải dùng timezone {TIMEZONE}")
    if set(frame["timezone"].dropna()) != {TIMEZONE}:
        raise ValueError(f"timezone metadata phải là {TIMEZONE}")
    if not (
        frame["training_feature_eligible"]
        == (frame["time"] < frame["event_at"])
    ).all():
        raise ValueError("training_feature_eligible không khớp thời điểm sự kiện")
    if (grid_distance_km(frame) > max_grid_distance_km).any():
        raise ValueError(f"Grid ERA5 lệch quá {max_grid_distance_km:g} km")


def validate_inputs(events: pd.DataFrame, locations: pd.DataFrame) -> None:
    missing_events = EVENT_REQUIRED_COLUMNS.difference(events.columns)
    missing_locations = LOCATION_REQUIRED_COLUMNS.difference(locations.columns)
    if missing_events:
        raise ValueError(f"Events thiếu cột: {sorted(missing_events)}")
    if missing_locations:
        raise ValueError(f"Locations thiếu cột: {sorted(missing_locations)}")
    if events.empty or events["event_id"].isna().any() or not events["event_id"].is_unique:
        raise ValueError("event_id phải có giá trị và không trùng")
    if not events["event_id"].astype(str).map(
        lambda value: EVENT_ID_PATTERN.fullmatch(value) is not None
    ).all():
        raise ValueError("event_id chứa ký tự không an toàn cho partition")
    if events[list(EVENT_REQUIRED_COLUMNS)].isna().any().any():
        raise ValueError("Các cột event bắt buộc không được rỗng")
    if "record_eligible_for_era5" not in events:
        raise ValueError("Events thiếu record_eligible_for_era5")
    if not pd.api.types.is_bool_dtype(events["record_eligible_for_era5"]):
        raise ValueError("record_eligible_for_era5 phải có kiểu boolean")
    if not events["record_eligible_for_era5"].astype(bool).all():
        raise ValueError(
            "ERA5 windows chỉ nhận sự kiện đã xác minh độ chính xác cấp ngày"
        )
    if locations.empty or locations["location_id"].isna().any() or not locations["location_id"].is_unique:
        raise ValueError("location_id phải có giá trị và không trùng")
    if not locations["latitude"].between(-90, 90).all():
        raise ValueError("latitude ngoài khoảng -90..90")
    if not locations["longitude"].between(-180, 180).all():
        raise ValueError("longitude ngoài khoảng -180..180")


def event_manifest(
    event: dict,
    events_path: Path,
    locations_path: Path,
    batch_size: int,
    pre_hours: int,
    post_hours: int,
) -> dict:
    return {
        "dataset": "dien_bien_era5_event_weather_context",
        "source": "Open-Meteo Historical Weather API",
        "model": MODEL,
        "timezone": TIMEZONE,
        "hourly_variables": HOURLY_VARIABLES,
        "batch_size": batch_size,
        "window_policy": {
            "anchor": "event_date 00:00 local",
            "pre_hours": pre_hours,
            "post_hours": post_hours,
            "inclusive_endpoints": True,
            "fetch": "full dates then trim exact hours",
        },
        "events_sha256": file_sha256(events_path),
        "locations_sha256": file_sha256(locations_path),
        "event_provenance": {
            key: str(event[key])
            for key in (
                "event_id", "event_date", "spatial_precision", "source_name",
                "source_record_id", "source_url",
            )
        },
        "partitioning": ["event_id"],
    }


def ensure_manifest(path: Path, manifest: dict) -> None:
    if path.exists():
        existing = json.loads(path.read_text(encoding="utf-8"))
        if existing != manifest:
            raise ValueError(f"Manifest không tương thích: {path.parent.name}")
        return
    atomic_json(path, manifest)


def write_part(
    frame: pd.DataFrame,
    path: Path,
    event_id: str,
    expected_locations: pd.DataFrame,
    window_start: pd.Timestamp,
    event_at: pd.Timestamp,
    window_end: pd.Timestamp,
    spatial_precision: str,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".parquet.tmp")
    frame.to_parquet(temporary, index=False, engine="pyarrow", compression="zstd")
    validate_event_part(
        pd.read_parquet(temporary),
        event_id,
        expected_locations,
        window_start,
        event_at,
        window_end,
        spatial_precision,
    )
    temporary.replace(path)


def download_event_weather(
    events_path: Path,
    locations_path: Path,
    output_dir: Path,
    batch_size: int = 10,
    request_delay: float = 60.0,
    pre_hours: int = 72,
    post_hours: int = 48,
) -> tuple[int, int]:
    events = pd.read_parquet(events_path).sort_values("event_id")
    locations = pd.read_parquet(locations_path).sort_values("location_id")
    validate_inputs(events, locations)
    if batch_size <= 0 or request_delay < 0 or pre_hours < 0 or post_hours < 0:
        raise ValueError("Batch/window phải không âm và batch_size phải lớn hơn 0")
    session = create_session()
    downloaded = skipped = 0
    batch_count = math.ceil(len(locations) / batch_size)
    for event in events.to_dict("records"):
        event_id = str(event["event_id"])
        event_dir = output_dir / f"event_id={event_id}"
        ensure_manifest(
            event_dir / "_manifest.json",
            event_manifest(
                event, events_path, locations_path, batch_size, pre_hours, post_hours
            ),
        )
        (event_dir / "_SUCCESS").unlink(missing_ok=True)
        start, event_at, end = event_window(event["event_date"], pre_hours, post_hours)
        for batch_index, location_batch in batched(locations, batch_size):
            path = event_dir / f"part-{batch_index:03d}.parquet"
            if path.exists():
                try:
                    validate_event_part(
                        pd.read_parquet(path),
                        event_id,
                        location_batch,
                        start,
                        event_at,
                        end,
                        str(event["spatial_precision"]),
                    )
                    skipped += 1
                    continue
                except (OSError, ValueError):
                    path.unlink(missing_ok=True)
            responses = fetch_batch(
                session,
                location_batch,
                start.strftime("%Y-%m-%d"),
                end.strftime("%Y-%m-%d"),
            )
            frame = responses_to_frame(
                event,
                location_batch,
                responses,
                start,
                event_at,
                end,
                pd.Timestamp.now(tz=TIMEZONE),
            )
            write_part(
                frame,
                path,
                event_id,
                location_batch,
                start,
                event_at,
                end,
                str(event["spatial_precision"]),
            )
            downloaded += 1
            time.sleep(request_delay)
        atomic_json(
            event_dir / "_SUCCESS",
            {
                "event_id": event_id,
                "completed_at": pd.Timestamp.now(tz=TIMEZONE).isoformat(),
                "parts": batch_count,
                "locations": len(locations),
                "hours_per_location": int((end - start).total_seconds() / 3600) + 1,
            },
        )
    return downloaded, skipped


def validate_configuration(
    batch_size: int,
    request_delay: float,
    pre_hours: int,
    post_hours: int,
) -> None:
    if batch_size <= 0 or request_delay < 0 or pre_hours < 0 or post_hours < 0:
        raise ValueError(
            "Batch/window phải không âm và batch_size phải lớn hơn 0"
        )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Tải ERA5 theo cửa sổ chính xác quanh sự kiện Điện Biên."
    )
    parser.add_argument("--events", type=Path, required=True)
    parser.add_argument(
        "--locations", type=Path, default=Path("data/dien_bien_locations.parquet")
    )
    parser.add_argument("--output", type=Path, default=Path("data/event_weather"))
    parser.add_argument("--batch-size", type=int, default=10)
    parser.add_argument("--request-delay", type=float, default=60)
    parser.add_argument("--pre-hours", type=int, default=72)
    parser.add_argument("--post-hours", type=int, default=48)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    validate_configuration(
        args.batch_size,
        args.request_delay,
        args.pre_hours,
        args.post_hours,
    )
    events = pd.read_parquet(args.events)
    locations = pd.read_parquet(args.locations)
    validate_inputs(events, locations)
    print(
        f"{len(events)} sự kiện × {len(locations)} điểm × "
        f"{args.pre_hours + args.post_hours + 1} giờ"
    )
    if not args.dry_run:
        downloaded, skipped = download_event_weather(
            args.events,
            args.locations,
            args.output,
            args.batch_size,
            args.request_delay,
            args.pre_hours,
            args.post_hours,
        )
        print(f"Hoàn tất: tải {downloaded} part, bỏ qua {skipped} part")


if __name__ == "__main__":
    main()
