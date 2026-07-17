import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import pandas as pd

from pipeline.download.download_forecast import (
    download_forecast,
    responses_to_frame,
    validate_forecast_part,
)
from pipeline.transform.alert_rules import latest_forecast_partition


class ForecastPipelineTest(unittest.TestCase):
    def test_multiple_api_responses_keep_location_mapping_and_snapshot_key(self):
        locations = pd.DataFrame(
            {
                "location_id": [10, 20],
                "latitude": [21.1, 21.2],
                "longitude": [103.1, 103.2],
            }
        )
        snapshot_at = pd.Timestamp(
            "2026-07-17 10:00:00",
            tz="Asia/Ho_Chi_Minh",
        )
        retrieved_at = pd.Timestamp(
            "2026-07-17 10:05:00",
            tz="Asia/Ho_Chi_Minh",
        )
        hourly = {
            "time": ["2026-07-17T10:00", "2026-07-17T11:00"],
            "temperature_2m": [20.0, 21.0],
            "precipitation": [0.0, 1.0],
            "weather_code": [0, 61],
            "wind_speed_10m": [5.0, 6.0],
            "precipitation_probability": [10.0, 60.0],
            "wind_gusts_10m": [8.0, 9.0],
        }
        responses = [
            {
                "latitude": 21.12,
                "longitude": 103.12,
                "elevation": 500.0,
                "timezone": "Asia/Ho_Chi_Minh",
                "hourly": hourly,
            },
            {
                "latitude": 21.22,
                "longitude": 103.22,
                "elevation": 900.0,
                "timezone": "Asia/Ho_Chi_Minh",
                "hourly": hourly,
            },
        ]

        frame, warnings = responses_to_frame(
            locations,
            responses,
            snapshot_at,
            retrieved_at,
        )

        self.assertEqual(len(frame), 4)
        self.assertEqual(frame["location_id"].tolist(), [10, 10, 20, 20])
        self.assertEqual(frame["lead_hours"].tolist(), [0.0, 1.0, 0.0, 1.0])
        self.assertEqual(
            frame["snapshot_at"].unique().tolist(),
            [snapshot_at],
        )
        self.assertEqual(str(frame["valid_time"].dt.tz), "Asia/Ho_Chi_Minh")
        self.assertEqual(warnings, [])

    def test_forecast_part_rejects_non_hourly_cadence(self):
        locations = pd.DataFrame(
            {
                "location_id": [10],
                "latitude": [21.1],
                "longitude": [103.1],
            }
        )
        snapshot_at = pd.Timestamp(
            "2026-07-17 10:00:00",
            tz="Asia/Ho_Chi_Minh",
        )
        retrieved_at = snapshot_at + pd.Timedelta(minutes=5)
        response = {
            "latitude": 21.12,
            "longitude": 103.12,
            "elevation": 500.0,
            "timezone": "Asia/Ho_Chi_Minh",
            "hourly": {
                "time": [
                    "2026-07-17T10:00",
                    "2026-07-17T12:00",
                ],
                "temperature_2m": [20.0, 21.0],
                "precipitation": [0.0, 1.0],
                "weather_code": [0, 61],
                "wind_speed_10m": [5.0, 6.0],
            },
        }
        frame, _ = responses_to_frame(
            locations,
            [response],
            snapshot_at,
            retrieved_at,
        )

        with self.assertRaisesRegex(ValueError, "liên tục 1 giờ"):
            validate_forecast_part(frame, {10}, expected_hours=2)

    def test_latest_snapshot_ignores_newer_incomplete_partition(self):
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            complete = (
                root
                / "snapshot_date=2026-07-17"
                / "snapshot_time=1000"
            )
            incomplete = (
                root
                / "snapshot_date=2026-07-17"
                / "snapshot_time=1100"
            )
            complete.mkdir(parents=True)
            incomplete.mkdir(parents=True)
            (complete / "_SUCCESS").touch()
            (incomplete / "_manifest.json").touch()

            selected = latest_forecast_partition(root)

        self.assertEqual(selected.name, "snapshot_time=1000")

    def test_partial_snapshot_resumes_then_same_snapshot_is_idempotent(self):
        snapshot_at = pd.Timestamp(
            "2026-07-17 10:00:00",
            tz="Asia/Ho_Chi_Minh",
        )
        response = {
            "latitude": 21.1,
            "longitude": 103.1,
            "elevation": 500.0,
            "timezone": "Asia/Ho_Chi_Minh",
            "hourly": {
                "time": [
                    "2026-07-17T10:00",
                    "2026-07-17T11:00",
                ],
                "temperature_2m": [20.0, 21.0],
                "precipitation": [0.0, 1.0],
                "weather_code": [0, 61],
                "wind_speed_10m": [5.0, 6.0],
            },
        }
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            locations_path = root / "locations.parquet"
            output_path = root / "forecast"
            pd.DataFrame(
                {
                    "location_id": [10, 20],
                    "latitude": [21.1, 21.1],
                    "longitude": [103.1, 103.1],
                }
            ).to_parquet(locations_path, index=False)

            with patch(
                "pipeline.download.download_forecast.fetch_batch",
                side_effect=[[response], RuntimeError("interrupted")],
            ):
                with self.assertRaisesRegex(RuntimeError, "interrupted"):
                    download_forecast(
                        locations_path,
                        output_path,
                        snapshot_at,
                        batch_size=1,
                        forecast_hours=2,
                        request_delay=0,
                    )

            partition = (
                output_path
                / "snapshot_date=2026-07-17"
                / "snapshot_time=1000"
            )
            self.assertTrue((partition / "part-000.parquet").exists())
            self.assertFalse((partition / "_SUCCESS").exists())

            with patch(
                "pipeline.download.download_forecast.fetch_batch",
                return_value=[response],
            ) as resumed_fetch:
                _, downloaded, skipped = download_forecast(
                    locations_path,
                    output_path,
                    snapshot_at,
                    batch_size=1,
                    forecast_hours=2,
                    request_delay=0,
                )
            self.assertEqual((downloaded, skipped), (1, 1))
            self.assertEqual(resumed_fetch.call_count, 1)
            self.assertTrue((partition / "_SUCCESS").exists())

            with patch(
                "pipeline.download.download_forecast.fetch_batch"
            ) as idempotent_fetch:
                _, downloaded, skipped = download_forecast(
                    locations_path,
                    output_path,
                    snapshot_at,
                    batch_size=1,
                    forecast_hours=2,
                    request_delay=0,
                )
            self.assertEqual((downloaded, skipped), (0, 2))
            idempotent_fetch.assert_not_called()


if __name__ == "__main__":
    unittest.main()
