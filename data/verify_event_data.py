import argparse
import hashlib
import json
import sys
from pathlib import Path

import pandas as pd

try:
    from data.build_event_locations import select_spatial_representatives
    from data.download_event_weather import (
        event_window,
        validate_event_part,
    )
except ModuleNotFoundError:
    from build_event_locations import select_spatial_representatives
    from download_event_weather import event_window, validate_event_part

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_eligibility_dtype(events: pd.DataFrame) -> None:
    if "record_eligible_for_era5" not in events:
        raise ValueError("Event inventory thiếu record_eligible_for_era5")
    if not pd.api.types.is_bool_dtype(events["record_eligible_for_era5"]):
        raise ValueError("record_eligible_for_era5 phải có kiểu boolean")


def verify_event_inventory(
    events_path: Path,
    locations_path: Path,
) -> dict:
    events = pd.read_parquet(events_path)
    validate_eligibility_dtype(events)
    manifest = json.loads(
        events_path.with_suffix(".manifest.json").read_text(encoding="utf-8")
    )
    required = {
        "event_id",
        "event_date",
        "raw_hazard",
        "raw_province",
        "source_url",
        "source_sha256",
        "spatial_precision",
        "date_precision",
        "record_eligible_for_era5",
    }
    if missing := required.difference(events.columns):
        raise ValueError(f"Event inventory thiếu cột: {sorted(missing)}")
    if events.empty or not events["event_id"].is_unique:
        raise ValueError("Event inventory rỗng hoặc event_id bị trùng")
    if events["event_date"].isna().any():
        raise ValueError("Event dùng cho ERA5 phải có ngày đầy đủ")
    if set(events["province"]) != {"Điện Biên"}:
        raise ValueError("Event inventory chứa tỉnh ngoài Điện Biên")
    if set(events["spatial_precision"]) != {"province"}:
        raise ValueError("Độ chính xác không gian DesInventar không đúng")
    if len(set(events["source_sha256"])) != 1:
        raise ValueError("Event inventory có nhiều source fingerprint")
    if manifest["source_sha256"] != events["source_sha256"].iloc[0]:
        raise ValueError("Event manifest không khớp source fingerprint")
    if manifest["locations_sha256"] != file_sha256(locations_path):
        raise ValueError("Event manifest không khớp locations master")
    if manifest["accepted_rows"] != len(events):
        raise ValueError("Event row count không khớp manifest")
    if manifest["accepted_sha256"] != file_sha256(events_path):
        raise ValueError("Event Parquet không khớp manifest")
    rejected_path = events_path.with_name(manifest["rejected_path"])
    if not rejected_path.exists() or manifest["rejected_sha256"] != file_sha256(
        rejected_path
    ):
        raise ValueError("Rejected event artifact không khớp manifest")
    return {
        "events": len(events),
        "date_min": str(events["event_date"].min().date()),
        "date_max": str(events["event_date"].max().date()),
        "hazards": sorted(events["hazard"].unique().tolist()),
        "era5_eligible_events": int(
            events["record_eligible_for_era5"].astype(bool).sum()
        ),
    }


def verify_event_weather(
    events_path: Path,
    master_locations_path: Path,
    context_locations_path: Path,
    weather_root: Path,
    require_complete: bool = True,
) -> dict:
    events = pd.read_parquet(events_path).sort_values("event_id")
    locations = pd.read_parquet(context_locations_path).sort_values(
        "location_id"
    )
    locations_manifest = json.loads(
        context_locations_path.with_suffix(".manifest.json").read_text(
            encoding="utf-8"
        )
    )
    if locations_manifest["source_locations_sha256"] != file_sha256(
        master_locations_path
    ):
        raise ValueError("Event locations không khớp locations master")
    if locations_manifest["rows"] != len(locations):
        raise ValueError("Event locations row count không khớp manifest")
    if locations_manifest["selection_method"] != "deterministic_farthest_point_v1":
        raise ValueError("Event locations selection method không hợp lệ")
    if locations_manifest["artifact_sha256"] != file_sha256(
        context_locations_path
    ):
        raise ValueError("Event locations artifact không khớp manifest")
    expected_locations = select_spatial_representatives(
        pd.read_parquet(master_locations_path),
        count=len(locations),
    )
    pd.testing.assert_frame_equal(
        locations.reset_index(drop=True),
        expected_locations.sort_values("location_id").reset_index(drop=True),
        check_like=True,
    )
    complete_events = 0
    rows = 0
    eligible_events = events.loc[
        events["record_eligible_for_era5"].astype(bool)
    ]
    if require_complete and eligible_events.empty:
        raise ValueError(
            "Không có event nào được xác minh độ chính xác cấp ngày cho ERA5"
        )
    for event in eligible_events.to_dict("records"):
        event_dir = weather_root / f"event_id={event['event_id']}"
        success_path = event_dir / "_SUCCESS"
        if not success_path.exists():
            if require_complete:
                raise ValueError(f"Event weather chưa hoàn chỉnh: {event['event_id']}")
            continue
        manifest = json.loads(
            (event_dir / "_manifest.json").read_text(encoding="utf-8")
        )
        if manifest["events_sha256"] != file_sha256(events_path):
            raise ValueError("Event-weather manifest không khớp inventory")
        if manifest["locations_sha256"] != file_sha256(context_locations_path):
            raise ValueError("Event-weather manifest không khớp context locations")
        start, event_at, end = event_window(
            event["event_date"],
            manifest["window_policy"]["pre_hours"],
            manifest["window_policy"]["post_hours"],
        )
        parts = sorted(event_dir.glob("part-*.parquet"))
        expected_parts = (
            len(locations) + manifest["batch_size"] - 1
        ) // manifest["batch_size"]
        if len(parts) != expected_parts:
            raise ValueError(f"Số part không đúng cho {event['event_id']}")
        for index, part_path in enumerate(parts):
            batch = locations.iloc[
                index * manifest["batch_size"] :
                (index + 1) * manifest["batch_size"]
            ]
            part = pd.read_parquet(part_path)
            validate_event_part(
                part,
                event["event_id"],
                batch,
                start,
                event_at,
                end,
                event["spatial_precision"],
            )
            rows += len(part)
        complete_events += 1
    if require_complete and complete_events != len(eligible_events):
        raise ValueError("Chưa đủ event-weather partitions")
    return {
        "complete_events": complete_events,
        "expected_events": len(eligible_events),
        "weather_rows": rows,
        "context_locations": len(locations),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify P4 event data pipeline.")
    parser.add_argument(
        "--events",
        type=Path,
        default=Path("data/desinventar_events.parquet"),
    )
    parser.add_argument(
        "--locations",
        type=Path,
        default=Path("data/dien_bien_locations.parquet"),
    )
    parser.add_argument(
        "--context-locations",
        type=Path,
        default=Path("data/event_locations.parquet"),
    )
    parser.add_argument(
        "--weather-root",
        type=Path,
        default=Path("data/event_weather"),
    )
    parser.add_argument("--allow-incomplete-weather", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    inventory = verify_event_inventory(arguments.events, arguments.locations)
    weather = verify_event_weather(
        arguments.events,
        arguments.locations,
        arguments.context_locations,
        arguments.weather_root,
        require_complete=not arguments.allow_incomplete_weather,
    )
    print(
        "VERIFY PASS: "
        f"{inventory['events']} events ({inventory['date_min']}.."
        f"{inventory['date_max']}), "
        f"{inventory['era5_eligible_events']} date-verified | "
        f"{weather['complete_events']}/"
        f"{weather['expected_events']} weather windows | "
        f"{weather['weather_rows']} rows"
    )
