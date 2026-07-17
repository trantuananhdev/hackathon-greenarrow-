import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd

from pipeline.download.download_historical_weather import (
    HOURLY_VARIABLES,
    ensure_manifest,
    estimate_rows,
    format_duration,
    quarter_ranges,
    response_to_frame,
    write_batch,
)
from pipeline.verify.verify_weather_history import verify_dataset


class HistoricalWeatherPipelineTest(unittest.TestCase):
    def test_quarter_ranges_cover_leap_year_without_gaps(self):
        self.assertEqual(
            quarter_ranges(2024),
            [
                ("2024-01-01", "2024-03-31", "Q1"),
                ("2024-04-01", "2024-06-30", "Q2"),
                ("2024-07-01", "2024-09-30", "Q3"),
                ("2024-10-01", "2024-12-31", "Q4"),
            ],
        )

    def test_estimate_rows_for_85_locations_and_five_years(self):
        self.assertEqual(
            estimate_rows(85, "2021-01-01", "2025-12-31"),
            3_725_040,
        )

    def test_format_duration_for_progress_eta(self):
        self.assertEqual(format_duration(3_661), "1h 1m 1s")

    def test_estimate_rows_for_85_locations_and_ten_years(self):
        self.assertEqual(
            estimate_rows(85, "2016-01-01", "2025-12-31"),
            7_452_120,
        )

    def test_response_to_frame_keeps_location_mapping_and_vietnam_time(self):
        location = {
            "location_id": 7,
            "province": "Điện Biên",
            "old_admin_unit": "Xã Pá Khoang",
            "new_admin_unit": "Xã Mường Phăng",
            "latitude": 21.4394,
            "longitude": 103.0981,
        }
        response = {
            "latitude": 21.44,
            "longitude": 103.10,
            "elevation": 900,
            "hourly": {
                "time": ["2020-01-01T00:00", "2020-01-01T01:00"],
                "temperature_2m": [10.5, 10.0],
                "precipitation": [0.0, 0.2],
            },
        }

        frame = response_to_frame(location, response)

        self.assertEqual(len(frame), 2)
        self.assertEqual(frame.loc[0, "location_id"], 7)
        self.assertNotIn("old_admin_unit", frame.columns)
        self.assertNotIn("new_admin_unit", frame.columns)
        self.assertEqual(str(frame["time"].dt.tz), "Asia/Ho_Chi_Minh")
        self.assertEqual(
            frame.loc[0, "time"],
            pd.Timestamp("2020-01-01 00:00:00", tz="Asia/Ho_Chi_Minh"),
        )

    def test_write_rejects_an_all_null_required_variable(self):
        location = pd.DataFrame(
            [
                {
                    "location_id": 1,
                    "province": "Điện Biên",
                    "old_admin_unit": "Xã cũ",
                    "new_admin_unit": "Xã mới",
                    "latitude": 21.0,
                    "longitude": 103.0,
                }
            ]
        )
        hourly = {
            "time": ["2020-01-01T00:00"],
            **{name: [1.0] for name in HOURLY_VARIABLES},
        }
        hourly["precipitation"] = [None]
        response = {
            "latitude": 21.0,
            "longitude": 103.0,
            "elevation": 500,
            "hourly": hourly,
        }

        with self.assertRaisesRegex(ValueError, "rỗng theo location_id"):
            write_batch(
                location,
                [response],
                Path("unused.parquet"),
                expected_hours=1,
            )

    def test_quarterly_layout_and_manifest_pass_full_verifier(self):
        location = pd.DataFrame(
            [
                {
                    "location_id": 1,
                    "province": "Điện Biên",
                    "old_admin_unit": "Xã cũ",
                    "new_admin_unit": "Xã mới",
                    "latitude": 21.0,
                    "longitude": 103.0,
                }
            ]
        )
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            locations_path = root / "locations.parquet"
            dataset_path = root / "weather_history"
            location.to_parquet(locations_path, index=False)
            ensure_manifest(dataset_path, locations_path, 2024, 2024, 1)

            for start_date, end_date, quarter_label in quarter_ranges(2024):
                times = pd.date_range(
                    start_date,
                    pd.Timestamp(end_date) + pd.Timedelta(hours=23),
                    freq="h",
                )
                response = {
                    "latitude": 21.0,
                    "longitude": 103.0,
                    "elevation": 500,
                    "hourly": {
                        "time": times.strftime("%Y-%m-%dT%H:%M").tolist(),
                        **{
                            name: [1.0] * len(times)
                            for name in HOURLY_VARIABLES
                        },
                    },
                }
                write_batch(
                    location,
                    [response],
                    dataset_path
                    / "year=2024"
                    / f"q={quarter_label}"
                    / "part-000.parquet",
                    expected_hours=len(times),
                )

            result = verify_dataset(locations_path, dataset_path)

        self.assertEqual(result["parts"], 4)
        self.assertEqual(result["rows"], 8_784)
        self.assertEqual(result["locations"], 1)

    def test_reset_incompatible_manifest_only_removes_generated_layout(self):
        location = pd.DataFrame(
            [
                {
                    "location_id": 1,
                    "province": "Điện Biên",
                    "old_admin_unit": "Xã cũ",
                    "new_admin_unit": "Xã mới",
                    "latitude": 21.0,
                    "longitude": 103.0,
                }
            ]
        )
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            locations_path = root / "locations.parquet"
            dataset_path = root / "weather_history"
            legacy_part = dataset_path / "year=2016" / "part-000.parquet"
            unrelated_file = dataset_path / "README.txt"
            nested_unrelated_file = dataset_path / "year=2016" / "notes.txt"
            legacy_part.parent.mkdir(parents=True)
            legacy_part.touch()
            unrelated_file.write_text("keep", encoding="utf-8")
            nested_unrelated_file.write_text("keep", encoding="utf-8")
            (dataset_path / "_manifest.json").write_text(
                '{"dataset": "dien_bien_hourly_historical_weather"}',
                encoding="utf-8",
            )
            location.to_parquet(locations_path, index=False)

            ensure_manifest(
                dataset_path,
                locations_path,
                2021,
                2025,
                10,
                reset_incompatible=True,
            )

            self.assertFalse(legacy_part.exists())
            self.assertTrue(unrelated_file.exists())
            self.assertTrue(nested_unrelated_file.exists())
            self.assertTrue((dataset_path / "_manifest.json").exists())

    def test_reset_refuses_directory_not_owned_by_pipeline(self):
        location = pd.DataFrame(
            [
                {
                    "location_id": 1,
                    "province": "Điện Biên",
                    "old_admin_unit": "Xã cũ",
                    "new_admin_unit": "Xã mới",
                    "latitude": 21.0,
                    "longitude": 103.0,
                }
            ]
        )
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            locations_path = root / "locations.parquet"
            dataset_path = root / "weather_history"
            dataset_path.mkdir()
            location.to_parquet(locations_path, index=False)
            (dataset_path / "_manifest.json").write_text(
                '{"dataset": "someone_else"}',
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "không thuộc dataset"):
                ensure_manifest(
                    dataset_path,
                    locations_path,
                    2021,
                    2025,
                    10,
                    reset_incompatible=True,
                )


if __name__ == "__main__":
    unittest.main()
