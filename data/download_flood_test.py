import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import pandas as pd

from data.download_flood import (
    download_flood,
    latest_complete_partition,
    responses_to_frame,
    validate_flood_part,
)


class FloodPipelineTest(unittest.TestCase):
    def setUp(self):
        self.snapshot_at = pd.Timestamp(
            "2026-07-17 10:00", tz="Asia/Ho_Chi_Minh"
        )
        self.retrieved_at = self.snapshot_at + pd.Timedelta(minutes=5)
        self.points = pd.DataFrame(
            {
                "river_point_id": ["nam-rom-01", "nam-ou-01"],
                "river_name": ["Nậm Rốm", "Nậm Lay"],
                "point_name": ["Nậm Rốm 01", "Nậm Lay 01"],
                "latitude": [21.38, 22.05],
                "longitude": [103.02, 102.48],
            }
        )

    @staticmethod
    def response(latitude=21.38, longitude=103.02):
        return {
            "latitude": latitude,
            "longitude": longitude,
            "timezone": "GMT",
            "daily": {
                "time": ["2026-07-17", "2026-07-18"],
                "river_discharge": [10.0, 11.0],
                "river_discharge_mean": [10.0, 11.0],
                "river_discharge_median": [9.0, 10.0],
                "river_discharge_max": [14.0, 15.0],
                "river_discharge_min": [6.0, 7.0],
                "river_discharge_p25": [8.0, 9.0],
                "river_discharge_p75": [12.0, 13.0],
            },
        }

    def test_response_mapping_preserves_ids_and_date_type(self):
        frame = responses_to_frame(
            self.points,
            [self.response(), self.response(22.05, 102.48)],
            self.snapshot_at,
            self.retrieved_at,
        )
        self.assertEqual(
            frame["river_point_id"].tolist(),
            ["nam-rom-01", "nam-rom-01", "nam-ou-01", "nam-ou-01"],
        )
        self.assertEqual(str(frame["valid_date"].dtype), "object")
        self.assertEqual(frame["valid_date"].iloc[0].isoformat(), "2026-07-17")
        self.assertEqual(str(frame["snapshot_at"].dt.tz), "Asia/Ho_Chi_Minh")
        self.assertEqual(frame["river_name"].unique().tolist(), ["Nậm Rốm", "Nậm Lay"])

    def test_validation_rejects_bad_quantile_order(self):
        frame = responses_to_frame(
            self.points.iloc[:1],
            [self.response()],
            self.snapshot_at,
            self.retrieved_at,
        )
        frame.loc[0, "river_discharge_p25"] = 20.0
        with self.assertRaisesRegex(ValueError, "quantile"):
            validate_flood_part(
                frame,
                self.points.iloc[:1],
                expected_days=2,
                expected_snapshot_at=self.snapshot_at,
            )

    def test_validation_rejects_part_from_another_snapshot(self):
        frame = responses_to_frame(
            self.points.iloc[:1],
            [self.response()],
            self.snapshot_at,
            self.retrieved_at,
        )
        with self.assertRaisesRegex(ValueError, "snapshot_at"):
            validate_flood_part(
                frame,
                self.points.iloc[:1],
                expected_days=2,
                expected_snapshot_at=self.snapshot_at + pd.Timedelta(hours=1),
            )

    def test_validation_rejects_requested_coordinates_not_in_master(self):
        frame = responses_to_frame(
            self.points.iloc[:1],
            [self.response()],
            self.snapshot_at,
            self.retrieved_at,
        )
        frame["requested_latitude"] = 21.39
        with self.assertRaisesRegex(ValueError, "river-point master"):
            validate_flood_part(
                frame,
                self.points.iloc[:1],
                expected_days=2,
                expected_snapshot_at=self.snapshot_at,
            )

    def test_latest_complete_partition_ignores_incomplete(self):
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            old = root / "snapshot_date=2026-07-17" / "snapshot_time=1000"
            new = root / "snapshot_date=2026-07-17" / "snapshot_time=1100"
            old.mkdir(parents=True)
            new.mkdir(parents=True)
            (old / "_SUCCESS").touch()
            (new / "_manifest.json").touch()
            self.assertEqual(latest_complete_partition(root), old)

    def test_interrupted_snapshot_resumes_and_binds_input_hash(self):
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            points_path = root / "river_points.parquet"
            output_path = root / "flood"
            self.points.to_parquet(points_path, index=False)

            with patch(
                "data.download_flood.fetch_batch",
                side_effect=[
                    [self.response(22.05, 102.48)],
                    RuntimeError("interrupted"),
                ],
            ):
                with self.assertRaisesRegex(RuntimeError, "interrupted"):
                    download_flood(
                        points_path,
                        output_path,
                        self.snapshot_at,
                        batch_size=1,
                        forecast_days=2,
                        request_delay=0,
                    )

            partition = (
                output_path
                / "snapshot_date=2026-07-17"
                / "snapshot_time=1000"
            )
            self.assertFalse((partition / "_SUCCESS").exists())
            manifest = json.loads(
                (partition / "_manifest.json").read_text(encoding="utf-8")
            )
            self.assertIn("river_points_sha256", manifest)

            with patch(
                "data.download_flood.fetch_batch",
                return_value=[self.response()],
            ) as fetch:
                _, downloaded, skipped = download_flood(
                    points_path,
                    output_path,
                    self.snapshot_at,
                    batch_size=1,
                    forecast_days=2,
                    request_delay=0,
                )
            self.assertEqual((downloaded, skipped), (1, 1))
            self.assertEqual(fetch.call_count, 1)
            self.assertTrue((partition / "_SUCCESS").exists())

            first_part_path = partition / "part-000.parquet"
            corrupted = pd.read_parquet(first_part_path)
            corrupted["snapshot_at"] = self.snapshot_at + pd.Timedelta(hours=1)
            corrupted.to_parquet(first_part_path, index=False)
            with patch(
                "data.download_flood.fetch_batch",
                return_value=[self.response(22.05, 102.48)],
            ) as fetch:
                _, downloaded, skipped = download_flood(
                    points_path,
                    output_path,
                    self.snapshot_at,
                    batch_size=1,
                    forecast_days=2,
                    request_delay=0,
                )
            self.assertEqual((downloaded, skipped), (1, 1))
            self.assertEqual(fetch.call_count, 1)

            with patch("data.download_flood.fetch_batch") as fetch:
                _, downloaded, skipped = download_flood(
                    points_path,
                    output_path,
                    self.snapshot_at,
                    batch_size=1,
                    forecast_days=2,
                    request_delay=0,
                )
            self.assertEqual((downloaded, skipped), (0, 2))
            fetch.assert_not_called()


if __name__ == "__main__":
    unittest.main()
