import argparse
import hashlib
import json
import math
import time
from pathlib import Path

import numpy as np
import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


FLOOD_URL = "https://flood-api.open-meteo.com/v1/flood"
TIMEZONE = "Asia/Ho_Chi_Minh"
MODEL = "glofas_v4_seamless"
DAILY_VARIABLES = [
    "river_discharge",
    "river_discharge_mean",
    "river_discharge_median",
    "river_discharge_max",
    "river_discharge_min",
    "river_discharge_p25",
    "river_discharge_p75",
]
KEY_COLUMNS = ["river_point_id", "snapshot_at", "valid_date", "model"]


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


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalize_snapshot_at(value=None) -> pd.Timestamp:
    timestamp = pd.Timestamp.now(tz=TIMEZONE) if value is None else pd.Timestamp(value)
    if timestamp.tzinfo is None:
        timestamp = timestamp.tz_localize(TIMEZONE)
    else:
        timestamp = timestamp.tz_convert(TIMEZONE)
    return timestamp.floor("h")


def batched(frame: pd.DataFrame, batch_size: int):
    for start in range(0, len(frame), batch_size):
        yield start // batch_size, frame.iloc[start : start + batch_size]


def fetch_batch(
    session: requests.Session,
    points: pd.DataFrame,
    forecast_days: int,
) -> list[dict]:
    response = session.get(
        FLOOD_URL,
        params={
            "latitude": ",".join(points["latitude"].astype(str)),
            "longitude": ",".join(points["longitude"].astype(str)),
            "daily": ",".join(DAILY_VARIABLES),
            "forecast_days": forecast_days,
            "cell_selection": "nearest",
        },
        timeout=120,
    )
    response.raise_for_status()
    payload = response.json()
    return payload if isinstance(payload, list) else [payload]


def responses_to_frame(
    points: pd.DataFrame,
    responses: list[dict],
    snapshot_at: pd.Timestamp,
    retrieved_at: pd.Timestamp,
) -> pd.DataFrame:
    required_point_columns = {
        "river_point_id",
        "river_name",
        "point_name",
        "latitude",
        "longitude",
    }
    missing_point_columns = required_point_columns.difference(points.columns)
    if missing_point_columns:
        raise ValueError(
            f"River points missing columns: {sorted(missing_point_columns)}"
        )
    if len(responses) != len(points):
        raise ValueError(
            f"API returned {len(responses)} points for {len(points)} requests"
        )
    frames = []
    for point, response in zip(points.to_dict("records"), responses):
        daily = response.get("daily", {})
        if "time" not in daily or "river_discharge" not in daily:
            raise ValueError("Flood API response lacks time or river_discharge")
        frame = pd.DataFrame(daily).rename(columns={"time": "valid_date"})
        frame["valid_date"] = pd.to_datetime(frame["valid_date"]).dt.date
        for variable in DAILY_VARIABLES:
            if variable not in frame:
                frame[variable] = np.nan
        frame.insert(0, "river_point_id", str(point["river_point_id"]))
        frame["river_name"] = str(point["river_name"])
        frame["point_name"] = str(point["point_name"])
        frame["snapshot_at"] = snapshot_at
        frame["model"] = MODEL
        frame["requested_latitude"] = float(point["latitude"])
        frame["requested_longitude"] = float(point["longitude"])
        frame["grid_latitude"] = float(response["latitude"])
        frame["grid_longitude"] = float(response["longitude"])
        frame["retrieved_at"] = retrieved_at
        frames.append(frame)
    result = pd.concat(frames, ignore_index=True)
    validate_grid_distance(result)
    return result


def validate_grid_distance(frame: pd.DataFrame, max_distance_km: float = 20) -> None:
    lat1 = np.radians(frame["requested_latitude"].astype(float))
    lon1 = np.radians(frame["requested_longitude"].astype(float))
    lat2 = np.radians(frame["grid_latitude"].astype(float))
    lon2 = np.radians(frame["grid_longitude"].astype(float))
    value = (
        np.sin((lat2 - lat1) / 2) ** 2
        + np.cos(lat1) * np.cos(lat2) * np.sin((lon2 - lon1) / 2) ** 2
    )
    distance = 6_371 * 2 * np.arcsin(np.sqrt(value))
    if (distance > max_distance_km).any():
        raise ValueError(f"Flood grid is more than {max_distance_km:g} km from input")


def validate_flood_part(
    frame: pd.DataFrame,
    expected_points: pd.DataFrame,
    expected_days: int,
    expected_snapshot_at: pd.Timestamp,
    expected_model: str = MODEL,
) -> None:
    expected_point_ids = set(expected_points["river_point_id"].astype(str))
    required = set(KEY_COLUMNS + DAILY_VARIABLES[:1] + [
        "river_name", "point_name",
        "requested_latitude", "requested_longitude",
        "grid_latitude", "grid_longitude", "retrieved_at",
    ])
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"Missing flood columns: {sorted(missing)}")
    actual_ids = set(frame["river_point_id"].astype(str))
    if actual_ids != expected_point_ids:
        raise ValueError(f"Point coverage differs: {actual_ids} != {expected_point_ids}")
    expected_by_id = expected_points.assign(
        river_point_id=expected_points["river_point_id"].astype(str)
    ).set_index("river_point_id")
    for point_id, group in frame.groupby("river_point_id"):
        expected = expected_by_id.loc[str(point_id)]
        for column, master_column in [
            ("requested_latitude", "latitude"),
            ("requested_longitude", "longitude"),
        ]:
            if not np.isclose(
                float(group[column].iloc[0]),
                float(expected[master_column]),
                rtol=0,
                atol=1e-9,
            ):
                raise ValueError(
                    f"{point_id} {column} differs from river-point master"
                )
        for column in ["river_name", "point_name"]:
            if set(group[column].astype(str)) != {str(expected[column])}:
                raise ValueError(
                    f"{point_id} {column} differs from river-point master"
                )
    if frame.duplicated(KEY_COLUMNS).any():
        raise ValueError("Duplicate flood snapshot key")
    snapshots = pd.DatetimeIndex(frame["snapshot_at"].unique())
    expected_snapshot = pd.Timestamp(expected_snapshot_at)
    if len(snapshots) != 1 or snapshots[0] != expected_snapshot:
        raise ValueError("Flood part snapshot_at differs from partition manifest")
    models = set(frame["model"].astype(str))
    if models != {expected_model}:
        raise ValueError("Flood part model differs from partition manifest")
    if frame["river_discharge"].isna().any():
        raise ValueError("river_discharge contains null values")
    available_discharge = [
        column
        for column in DAILY_VARIABLES
        if column in frame and frame[column].notna().any()
    ]
    if (frame[available_discharge] < 0).any().any():
        raise ValueError("Flood discharge variables contain negative values")
    if str(frame["snapshot_at"].dt.tz) != TIMEZONE:
        raise ValueError(f"snapshot_at must use {TIMEZONE}")
    if str(frame["retrieved_at"].dt.tz) != TIMEZONE:
        raise ValueError(f"retrieved_at must use {TIMEZONE}")
    for point_id, group in frame.groupby("river_point_id"):
        for coordinate in [
            "requested_latitude",
            "requested_longitude",
            "grid_latitude",
            "grid_longitude",
        ]:
            if group[coordinate].nunique(dropna=False) != 1:
                raise ValueError(
                    f"{point_id} has varying {coordinate} within one snapshot"
                )
        dates = pd.to_datetime(group["valid_date"]).sort_values()
        if dates.nunique() != expected_days:
            raise ValueError(f"{point_id} does not have {expected_days} forecast days")
        if len(dates) > 1 and not (
            dates.diff().dropna() == pd.Timedelta(days=1)
        ).all():
            raise ValueError(f"{point_id} valid_date cadence is not daily")
        first_date = group["snapshot_at"].iloc[0].date()
        if any(value.date() < first_date for value in dates):
            raise ValueError(f"{point_id} has a forecast date before snapshot")
    quantiles = ["river_discharge_min", "river_discharge_p25",
                 "river_discharge_median", "river_discharge_p75",
                 "river_discharge_max"]
    if all(column in frame and frame[column].notna().all() for column in quantiles):
        values = frame[quantiles].to_numpy(dtype=float)
        if (np.diff(values, axis=1) < 0).any():
            raise ValueError("Flood discharge quantile ordering is invalid")
    validate_grid_distance(frame)


def snapshot_directory(output_dir: Path, snapshot_at: pd.Timestamp) -> Path:
    return (
        output_dir
        / f"snapshot_date={snapshot_at:%Y-%m-%d}"
        / f"snapshot_time={snapshot_at:%H%M}"
    )


def latest_complete_partition(output_dir: Path) -> Path:
    candidates = sorted(output_dir.glob("snapshot_date=*/snapshot_time=*"))
    complete = [path for path in candidates if (path / "_SUCCESS").exists()]
    if not complete:
        raise FileNotFoundError(f"No complete flood snapshot in {output_dir}")
    return complete[-1]


def ensure_manifest(
    partition: Path,
    points_path: Path,
    snapshot_at: pd.Timestamp,
    batch_size: int,
    forecast_days: int,
) -> None:
    manifest = {
        "dataset": "dien_bien_daily_flood_snapshot",
        "source": "Open-Meteo Flood API (GloFAS)",
        "model": MODEL,
        "timezone": TIMEZONE,
        "snapshot_at": snapshot_at.isoformat(),
        "forecast_days": forecast_days,
        "batch_size": batch_size,
        "daily_variables": DAILY_VARIABLES,
        "cell_selection": "nearest",
        "river_points_sha256": file_sha256(points_path),
        "partitioning": ["snapshot_date", "snapshot_time"],
    }
    partition.mkdir(parents=True, exist_ok=True)
    path = partition / "_manifest.json"
    if path.exists():
        if json.loads(path.read_text(encoding="utf-8")) != manifest:
            raise ValueError("Existing flood snapshot manifest is incompatible")
        return
    temporary = path.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    temporary.replace(path)


def write_part(
    frame: pd.DataFrame,
    output_path: Path,
    expected_points: pd.DataFrame,
    expected_days: int,
    expected_snapshot_at: pd.Timestamp,
) -> None:
    temporary = output_path.with_suffix(".parquet.tmp")
    frame.to_parquet(temporary, index=False, compression="zstd")
    validate_flood_part(
        pd.read_parquet(temporary),
        expected_points,
        expected_days,
        expected_snapshot_at,
    )
    temporary.replace(output_path)


def download_flood(
    points_path: Path,
    output_dir: Path,
    snapshot_at: pd.Timestamp,
    batch_size: int = 10,
    forecast_days: int = 30,
    request_delay: float = 5,
) -> tuple[Path, int, int]:
    points = pd.read_parquet(points_path).sort_values("river_point_id")
    required = {
        "river_point_id",
        "river_name",
        "point_name",
        "latitude",
        "longitude",
    }
    if missing := required.difference(points.columns):
        raise ValueError(f"Missing river point columns: {sorted(missing)}")
    if points["river_point_id"].astype(str).duplicated().any():
        raise ValueError("river_point_id must be unique")
    if batch_size <= 0 or forecast_days <= 0:
        raise ValueError("batch_size and forecast_days must be positive")
    partition = snapshot_directory(output_dir, snapshot_at)
    ensure_manifest(
        partition, points_path, snapshot_at, batch_size, forecast_days
    )
    # A prior success marker is not trustworthy while its parts are revalidated.
    # It is recreated atomically only after every part passes validation.
    (partition / "_SUCCESS").unlink(missing_ok=True)
    session = create_session()
    downloaded = skipped = 0
    batch_count = math.ceil(len(points) / batch_size)
    for batch_index, batch in batched(points, batch_size):
        path = partition / f"part-{batch_index:03d}.parquet"
        if path.exists():
            try:
                validate_flood_part(
                    pd.read_parquet(path),
                    batch,
                    forecast_days,
                    snapshot_at,
                )
                skipped += 1
                continue
            except (OSError, ValueError):
                path.unlink(missing_ok=True)
        responses = fetch_batch(session, batch, forecast_days)
        frame = responses_to_frame(
            batch,
            responses,
            snapshot_at,
            pd.Timestamp.now(tz=TIMEZONE),
        )
        write_part(frame, path, batch, forecast_days, snapshot_at)
        downloaded += 1
        if batch_index + 1 < batch_count:
            time.sleep(request_delay)
    success = partition / "_SUCCESS"
    temporary = success.with_suffix(".tmp")
    temporary.write_text(
        json.dumps(
            {
                "snapshot_at": snapshot_at.isoformat(),
                "completed_at": pd.Timestamp.now(tz=TIMEZONE).isoformat(),
                "parts": batch_count,
                "river_points": len(points),
                "rows": len(points) * forecast_days,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    temporary.replace(success)
    return partition, downloaded, skipped


def main() -> None:
    parser = argparse.ArgumentParser(description="Download daily GloFAS flood forecast.")
    parser.add_argument("--river-points", type=Path, default=Path("data/river_points.parquet"))
    parser.add_argument("--output", type=Path, default=Path("data/flood"))
    parser.add_argument("--snapshot-at")
    parser.add_argument("--batch-size", type=int, default=10)
    parser.add_argument("--forecast-days", type=int, default=30)
    parser.add_argument("--request-delay", type=float, default=5)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    snapshot_at = normalize_snapshot_at(args.snapshot_at)
    points = pd.read_parquet(args.river_points)
    print(
        f"Snapshot {snapshot_at.isoformat()} | {len(points)} river points | "
        f"{math.ceil(len(points) / args.batch_size)} parts | "
        f"{len(points) * args.forecast_days:,} rows"
    )
    if not args.dry_run:
        partition, downloaded, skipped = download_flood(
            args.river_points,
            args.output,
            snapshot_at,
            args.batch_size,
            args.forecast_days,
            args.request_delay,
        )
        print(f"Downloaded {downloaded}, skipped {skipped} -> {partition}")


if __name__ == "__main__":
    main()
