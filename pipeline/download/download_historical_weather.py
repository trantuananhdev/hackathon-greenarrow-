import argparse
import calendar
import hashlib
import json
import math
import re
import sys
import time
from datetime import date
from pathlib import Path

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


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


def quarter_ranges(year: int) -> list[tuple[str, str, str]]:
    ranges = []
    for quarter, start_month in enumerate((1, 4, 7, 10), start=1):
        end_month = start_month + 2
        end_day = calendar.monthrange(year, end_month)[1]
        ranges.append(
            (
                f"{year}-{start_month:02d}-01",
                f"{year}-{end_month:02d}-{end_day:02d}",
                f"Q{quarter}",
            )
        )
    return ranges


def format_duration(seconds: float) -> str:
    total_seconds = max(0, int(seconds))
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours}h {minutes}m {seconds}s"


def estimate_rows(location_count: int, start_date: str, end_date: str) -> int:
    start = date.fromisoformat(start_date)
    end = date.fromisoformat(end_date)
    if end < start:
        raise ValueError("end_date phải lớn hơn hoặc bằng start_date")
    return location_count * ((end - start).days + 1) * 24


def response_to_frame(location: dict, response: dict) -> pd.DataFrame:
    hourly = response["hourly"]
    frame = pd.DataFrame(hourly)
    frame["time"] = pd.to_datetime(frame["time"]).dt.tz_localize(
        TIMEZONE,
        ambiguous="raise",
        nonexistent="raise",
    )
    frame.insert(0, "location_id", int(location["location_id"]))
    frame["grid_latitude"] = float(response["latitude"])
    frame["grid_longitude"] = float(response["longitude"])
    frame["grid_elevation"] = float(response["elevation"])
    return frame


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


def fetch_batch(
    session: requests.Session,
    locations: pd.DataFrame,
    start_date: str,
    end_date: str,
) -> list[dict]:
    params = {
        "latitude": ",".join(locations["latitude"].astype(str)),
        "longitude": ",".join(locations["longitude"].astype(str)),
        "start_date": start_date,
        "end_date": end_date,
        "hourly": ",".join(HOURLY_VARIABLES),
        "timezone": TIMEZONE,
        "models": MODEL,
    }
    response = session.get(ARCHIVE_URL, params=params, timeout=180)
    response.raise_for_status()
    payload = response.json()
    return payload if isinstance(payload, list) else [payload]


def write_batch(
    locations: pd.DataFrame,
    responses: list[dict],
    output_path: Path,
    expected_hours: int | None = None,
) -> int:
    if len(responses) != len(locations):
        raise ValueError(
            f"API trả {len(responses)} vị trí cho {len(locations)} vị trí yêu cầu"
        )
    frames = [
        response_to_frame(location, response)
        for location, response in zip(
            locations.to_dict(orient="records"),
            responses,
        )
    ]
    combined = pd.concat(frames, ignore_index=True)
    required_weather_columns = {"time", *HOURLY_VARIABLES}
    missing_columns = required_weather_columns.difference(combined.columns)
    if missing_columns:
        raise ValueError(
            f"API thiếu cột thời tiết: {sorted(missing_columns)}"
        )
    all_null_variables = {}
    for location_id, group in combined.groupby("location_id"):
        missing_for_location = [
            name for name in HOURLY_VARIABLES if group[name].isna().all()
        ]
        if missing_for_location:
            all_null_variables[int(location_id)] = missing_for_location
    if all_null_variables:
        raise ValueError(
            f"API trả biến rỗng theo location_id: {all_null_variables}"
        )
    if combined.duplicated(["location_id", "time"]).any():
        raise ValueError("API trả timestamp trùng trong cùng một địa điểm")
    if expected_hours is not None:
        counts = combined.groupby("location_id")["time"].nunique()
        invalid = counts[counts != expected_hours]
        if not invalid.empty:
            raise ValueError(
                f"Thiếu giờ ở location_id: {invalid.to_dict()} "
                f"(cần {expected_hours})"
            )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = output_path.with_suffix(".parquet.tmp")
    combined.to_parquet(
        temporary_path,
        index=False,
        engine="pyarrow",
        compression="zstd",
    )
    written = pd.read_parquet(
        temporary_path,
        columns=["location_id", "time"],
    )
    if len(written) != len(combined):
        temporary_path.unlink(missing_ok=True)
        raise ValueError("Số dòng Parquet sau khi ghi không khớp dữ liệu nguồn")
    temporary_path.replace(output_path)
    return len(combined)


def validate_existing_part(
    path: Path,
    expected_hours: int,
    expected_location_ids: set[int],
) -> None:
    required = {"location_id", "time", *HOURLY_VARIABLES}
    frame = pd.read_parquet(path)
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"Part thiếu cột: {sorted(missing)}")
    actual_ids = set(frame["location_id"].astype(int).unique())
    if actual_ids != expected_location_ids:
        raise ValueError(
            f"Part chứa location_id {actual_ids}, cần {expected_location_ids}"
        )
    if frame.duplicated(["location_id", "time"]).any():
        raise ValueError("Part chứa khóa (location_id, time) trùng")
    counts = frame.groupby("location_id")["time"].nunique()
    if not (counts == expected_hours).all():
        raise ValueError(f"Part thiếu giờ: {counts.to_dict()}")
    all_null = {}
    for location_id, group in frame.groupby("location_id"):
        missing_for_location = [
            name for name in HOURLY_VARIABLES if group[name].isna().all()
        ]
        if missing_for_location:
            all_null[int(location_id)] = missing_for_location
    if all_null:
        raise ValueError(f"Part có biến rỗng theo location_id: {all_null}")


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def ensure_manifest(
    output_dir: Path,
    locations_path: Path,
    start_year: int,
    end_year: int,
    batch_size: int,
    reset_incompatible: bool = False,
) -> None:
    manifest = {
        "dataset": "dien_bien_hourly_historical_weather",
        "source": "Open-Meteo Historical Weather API",
        "model": MODEL,
        "timezone": TIMEZONE,
        "hourly_variables": HOURLY_VARIABLES,
        "start_year": start_year,
        "end_year": end_year,
        "batch_size": batch_size,
        "partitioning": ["year", "q"],
        "locations_sha256": file_sha256(locations_path),
        "units": {
            "temperature_2m": "°C",
            "relative_humidity_2m": "%",
            "precipitation": "mm",
            "rain": "mm",
            "wind_speed_10m": "km/h",
            "soil_moisture_0_to_7cm": "m³/m³",
        },
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = output_dir / "_manifest.json"
    if manifest_path.exists():
        existing = json.loads(manifest_path.read_text(encoding="utf-8"))
        if existing != manifest:
            if not reset_incompatible:
                raise ValueError(
                    "Cấu hình hiện tại khác _manifest.json; "
                    "dùng --reset-incompatible để xóa manifest/part "
                    "do pipeline tạo, hoặc chọn output directory mới."
                )
            reset_generated_dataset(output_dir, existing)
            output_dir.mkdir(parents=True, exist_ok=True)
        else:
            return
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def reset_generated_dataset(output_dir: Path, existing_manifest: dict) -> None:
    """Remove only weather part files owned by this pipeline."""
    if existing_manifest.get("dataset") != "dien_bien_hourly_historical_weather":
        raise ValueError(
            "Không reset vì manifest không thuộc dataset thời tiết Điện Biên."
        )
    output_root = output_dir.resolve()
    generated_parts = []
    managed_quarter_dirs = []
    managed_year_dirs = []
    for year_dir in output_dir.iterdir():
        if not (
            year_dir.is_dir()
            and re.fullmatch(r"year=\d{4}", year_dir.name)
        ):
            continue
        managed_year_dirs.append(year_dir)
        generated_parts.extend(year_dir.glob("part-*.parquet"))
        for quarter_dir in year_dir.iterdir():
            if (
                quarter_dir.is_dir()
                and re.fullmatch(r"q=Q[1-4]", quarter_dir.name)
            ):
                managed_quarter_dirs.append(quarter_dir)
                generated_parts.extend(quarter_dir.glob("part-*.parquet"))
    for part_path in generated_parts:
        resolved_part = part_path.resolve()
        if not resolved_part.is_relative_to(output_root):
            raise ValueError(f"Part nằm ngoài output directory: {part_path}")
        part_path.unlink()
    (output_dir / "_manifest.json").unlink(missing_ok=True)
    for quarter_dir in managed_quarter_dirs:
        if not any(quarter_dir.iterdir()):
            quarter_dir.rmdir()
    for year_dir in managed_year_dirs:
        if not any(year_dir.iterdir()):
            year_dir.rmdir()


def download_history(
    locations_path: Path,
    output_dir: Path,
    start_year: int,
    end_year: int,
    batch_size: int,
    request_delay: float,
    overwrite: bool = False,
    reset_incompatible: bool = False,
) -> tuple[int, int]:
    locations = pd.read_parquet(locations_path).sort_values("location_id")
    required = {
        "location_id",
        "province",
        "old_admin_unit",
        "new_admin_unit",
        "latitude",
        "longitude",
    }
    missing = required.difference(locations.columns)
    if missing:
        raise ValueError(f"Thiếu cột trong locations Parquet: {sorted(missing)}")
    if locations.empty:
        raise ValueError("Locations Parquet không có bản ghi")
    if locations["location_id"].isna().any() or not locations["location_id"].is_unique:
        raise ValueError("location_id phải có giá trị và không trùng")
    if not locations["latitude"].between(-90, 90).all():
        raise ValueError("latitude nằm ngoài khoảng -90..90")
    if not locations["longitude"].between(-180, 180).all():
        raise ValueError("longitude nằm ngoài khoảng -180..180")
    if batch_size <= 0:
        raise ValueError("batch_size phải lớn hơn 0")
    if request_delay < 0:
        raise ValueError("request_delay không được âm")

    ensure_manifest(
        output_dir,
        locations_path,
        start_year,
        end_year,
        batch_size,
        reset_incompatible,
    )

    session = create_session()
    downloaded_rows = 0
    skipped_parts = 0
    downloaded_parts = 0
    completed_parts = 0
    total_parts = (
        (end_year - start_year + 1)
        * 4
        * math.ceil(len(locations) / batch_size)
    )
    started_at = time.monotonic()

    for year in range(start_year, end_year + 1):
        for start_date, end_date, quarter_label in quarter_ranges(year):
            expected_hours = estimate_rows(1, start_date, end_date)
            for batch_index, location_batch in batched(locations, batch_size):
                output_path = (
                    output_dir
                    / f"year={year}"
                    / f"q={quarter_label}"
                    / f"part-{batch_index:03d}.parquet"
                )
                if output_path.exists() and not overwrite:
                    try:
                        validate_existing_part(
                            output_path,
                            expected_hours,
                            set(location_batch["location_id"].astype(int)),
                        )
                        skipped_parts += 1
                        completed_parts += 1
                        elapsed = time.monotonic() - started_at
                        if completed_parts == total_parts:
                            eta_text = format_duration(0)
                        elif downloaded_parts:
                            eta_text = format_duration(
                                elapsed
                                / downloaded_parts
                                * (total_parts - completed_parts)
                            )
                        else:
                            eta_text = "đang tính"
                        percentage = completed_parts / total_parts * 100
                        print(
                            f"[{completed_parts}/{total_parts} | "
                            f"{percentage:5.1f}% | ETA {eta_text}] "
                            f"{year} {quarter_label} batch {batch_index + 1}/"
                            f"{math.ceil(len(locations) / batch_size)}: "
                            f"bỏ qua part đã xác thực"
                        )
                        continue
                    except (OSError, ValueError):
                        output_path.unlink(missing_ok=True)

                responses = fetch_batch(
                    session,
                    location_batch,
                    start_date,
                    end_date,
                )
                row_count = write_batch(
                    location_batch,
                    responses,
                    output_path,
                    expected_hours,
                )
                downloaded_rows += row_count
                downloaded_parts += 1
                completed_parts += 1
                elapsed = time.monotonic() - started_at
                seconds_per_download = elapsed / downloaded_parts
                eta = seconds_per_download * (total_parts - completed_parts)
                percentage = completed_parts / total_parts * 100
                print(
                    f"[{completed_parts}/{total_parts} | {percentage:5.1f}% | "
                    f"ETA {format_duration(eta)}] "
                    f"{year} {quarter_label} batch {batch_index + 1}/"
                    f"{math.ceil(len(locations) / batch_size)}: "
                    f"{row_count:,} dòng -> {output_path}"
                )
                time.sleep(request_delay)

    return downloaded_rows, skipped_parts


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Tải ERA5 theo giờ và lưu Parquet phân vùng theo năm."
    )
    parser.add_argument(
        "--locations",
        type=Path,
        default=Path("data/reference/dien_bien_locations.parquet"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/weather/history"),
    )
    parser.add_argument("--start-year", type=int, default=2021)
    parser.add_argument("--end-year", type=int, default=2025)
    parser.add_argument(
        "--batch-size",
        type=int,
        default=10,
        help="Mặc định chia 10 điểm/request để giảm payload.",
    )
    parser.add_argument(
        "--request-delay",
        type=float,
        default=60,
        help="Số giây nghỉ giữa các request để tránh HTTP 429.",
    )
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument(
        "--reset-incompatible",
        action="store_true",
        help=(
            "Xóa _manifest.json và các partition year= do pipeline tạo "
            "nếu cấu hình cũ không tương thích."
        ),
    )
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.end_year < args.start_year:
        raise ValueError("end-year phải lớn hơn hoặc bằng start-year")

    locations = pd.read_parquet(args.locations)
    expected = estimate_rows(
        len(locations),
        f"{args.start_year}-01-01",
        f"{args.end_year}-12-31",
    )
    parts = (
        math.ceil(len(locations) / args.batch_size)
        * 4
        * (args.end_year - args.start_year + 1)
    )
    print(
        f"{len(locations)} địa điểm | {args.start_year}-{args.end_year} | "
        f"ước tính {expected:,} dòng | {parts} part"
    )
    if args.dry_run:
        return

    downloaded_rows, skipped_parts = download_history(
        args.locations,
        args.output,
        args.start_year,
        args.end_year,
        args.batch_size,
        args.request_delay,
        args.overwrite,
        args.reset_incompatible,
    )
    print(
        f"Hoàn tất lượt chạy: tải {downloaded_rows:,} dòng, "
        f"bỏ qua {skipped_parts} part đã có."
    )


if __name__ == "__main__":
    main()
