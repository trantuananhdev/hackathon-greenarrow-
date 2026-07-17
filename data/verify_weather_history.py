import argparse
import json
import math
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq

from download_historical_weather import (
    HOURLY_VARIABLES,
    MODEL,
    TIMEZONE,
    estimate_rows,
    validate_existing_part,
)


def verify_dataset(
    locations_path: Path,
    dataset_path: Path,
) -> dict:
    manifest_path = dataset_path / "_manifest.json"
    if not manifest_path.exists():
        raise ValueError("Thiếu _manifest.json")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    if manifest["model"] != MODEL:
        raise ValueError(f"Model phải là {MODEL}, nhận {manifest['model']}")
    if manifest["timezone"] != TIMEZONE:
        raise ValueError(
            f"Timezone phải là {TIMEZONE}, nhận {manifest['timezone']}"
        )
    if manifest["hourly_variables"] != HOURLY_VARIABLES:
        raise ValueError("Danh sách biến trong manifest không khớp pipeline")

    locations = pd.read_parquet(locations_path).sort_values("location_id")
    batch_size = int(manifest["batch_size"])
    start_year = int(manifest["start_year"])
    end_year = int(manifest["end_year"])
    expected_parts = (
        math.ceil(len(locations) / batch_size)
        * (end_year - start_year + 1)
    )
    actual_files = sorted(dataset_path.glob("year=*/part-*.parquet"))
    if len(actual_files) != expected_parts:
        raise ValueError(
            f"Thiếu part: có {len(actual_files)}, cần {expected_parts}"
        )

    total_rows = 0
    for year in range(start_year, end_year + 1):
        expected_hours = estimate_rows(
            1,
            f"{year}-01-01",
            f"{year}-12-31",
        )
        for batch_index, start in enumerate(
            range(0, len(locations), batch_size)
        ):
            location_batch = locations.iloc[start : start + batch_size]
            path = (
                dataset_path
                / f"year={year}"
                / f"part-{batch_index:03d}.parquet"
            )
            if not path.exists():
                raise ValueError(f"Thiếu {path}")
            validate_existing_part(
                path,
                expected_hours,
                set(location_batch["location_id"].astype(int)),
            )
            total_rows += pq.ParquetFile(path).metadata.num_rows

    expected_rows = estimate_rows(
        len(locations),
        f"{start_year}-01-01",
        f"{end_year}-12-31",
    )
    if total_rows != expected_rows:
        raise ValueError(
            f"Tổng dòng {total_rows:,}, cần {expected_rows:,}"
        )
    return {
        "locations": len(locations),
        "parts": len(actual_files),
        "rows": total_rows,
        "start_year": start_year,
        "end_year": end_year,
        "model": MODEL,
        "timezone": TIMEZONE,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--locations",
        type=Path,
        default=Path("data/dien_bien_locations.parquet"),
    )
    parser.add_argument(
        "--dataset",
        type=Path,
        default=Path("data/weather_history"),
    )
    args = parser.parse_args()
    result = verify_dataset(args.locations, args.dataset)
    print(
        "VERIFY PASS: "
        f"{result['rows']:,} dòng | {result['parts']} part | "
        f"{result['locations']} địa điểm | "
        f"{result['start_year']}-{result['end_year']} | "
        f"{result['model']} | {result['timezone']}"
    )


if __name__ == "__main__":
    main()
