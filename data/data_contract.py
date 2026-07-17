from collections.abc import Iterable

import pandas as pd


TIMEZONE = "Asia/Ho_Chi_Minh"
LOCATION_ID_COLUMN = "location_id"
FORECAST_KEY = ["location_id", "snapshot_at", "valid_time", "model"]
FORECAST_METADATA = [
    "lead_hours",
    "grid_latitude",
    "grid_longitude",
    "grid_elevation",
    "timezone",
    "retrieved_at",
]
FORECAST_REQUIRED_VARIABLES = [
    "temperature_2m",
    "precipitation",
    "weather_code",
    "wind_speed_10m",
]
FORECAST_OPTIONAL_VARIABLES = [
    "precipitation_probability",
    "wind_gusts_10m",
]


def validate_output(
    frame: pd.DataFrame,
    required_keys: Iterable[str],
    required_columns: Iterable[str],
) -> None:
    required = set(required_keys) | set(required_columns)
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"Thiếu cột bắt buộc: {sorted(missing)}")
    if frame.empty:
        raise ValueError("Output không có bản ghi")


def validate_no_all_null_variables(
    frame: pd.DataFrame,
    variable_columns: Iterable[str],
    *,
    optional: bool = False,
) -> list[str]:
    all_null = [name for name in variable_columns if frame[name].isna().all()]
    if all_null and not optional:
        raise ValueError(f"Biến bắt buộc rỗng hoàn toàn: {all_null}")
    return [
        f"Biến tùy chọn rỗng hoàn toàn: {name}"
        for name in all_null
    ]


def validate_no_duplicate_keys(
    frame: pd.DataFrame,
    key_columns: Iterable[str],
) -> None:
    keys = list(key_columns)
    if frame.duplicated(keys).any():
        raise ValueError(f"Output có khóa trùng: {keys}")


def validate_location_ids(
    frame: pd.DataFrame,
    expected_ids: set[int],
) -> None:
    actual_ids = set(frame[LOCATION_ID_COLUMN].astype(int).unique())
    if actual_ids != expected_ids:
        raise ValueError(
            f"location_id thực tế {actual_ids}, cần {expected_ids}"
        )


def validate_timezone(
    frame: pd.DataFrame,
    time_column: str,
    timezone: str = TIMEZONE,
) -> None:
    dtype = frame[time_column].dtype
    if not isinstance(dtype, pd.DatetimeTZDtype) or str(dtype.tz) != timezone:
        raise ValueError(
            f"{time_column} phải có timezone {timezone}, nhận {dtype}"
        )


def validate_forecast_output(
    frame: pd.DataFrame,
    expected_location_ids: set[int],
) -> list[str]:
    required_columns = [
        *FORECAST_METADATA,
        *FORECAST_REQUIRED_VARIABLES,
        *FORECAST_OPTIONAL_VARIABLES,
    ]
    validate_output(frame, FORECAST_KEY, required_columns)
    validate_no_duplicate_keys(frame, FORECAST_KEY)
    validate_location_ids(frame, expected_location_ids)
    for time_column in ("snapshot_at", "valid_time", "retrieved_at"):
        validate_timezone(frame, time_column)
    if set(frame["timezone"].dropna().unique()) != {TIMEZONE}:
        raise ValueError(f"timezone metadata phải là {TIMEZONE}")
    expected_lead_hours = (
        frame["valid_time"] - frame["snapshot_at"]
    ).dt.total_seconds() / 3600
    invalid_lead = (frame["lead_hours"] - expected_lead_hours).abs() > 1e-6
    if invalid_lead.any():
        raise ValueError("lead_hours không khớp valid_time - snapshot_at")
    for location_id, group in frame.groupby(LOCATION_ID_COLUMN):
        try:
            validate_no_all_null_variables(
                group,
                FORECAST_REQUIRED_VARIABLES,
            )
        except ValueError as error:
            raise ValueError(
                f"location_id {int(location_id)}: {error}"
            ) from error
    return validate_no_all_null_variables(
        frame,
        FORECAST_OPTIONAL_VARIABLES,
        optional=True,
    )
