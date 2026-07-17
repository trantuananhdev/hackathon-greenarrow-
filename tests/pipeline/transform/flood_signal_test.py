import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd

from pipeline.transform.flood_signal import build_flood_signals, generate_signals


class FloodSignalTest(unittest.TestCase):
    def test_missing_source_manifest_does_not_replace_existing_output(self):
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            partition = root / "snapshot"
            partition.mkdir()
            part = partition / "part-000.parquet"
            pd.DataFrame({"value": [1]}).to_parquet(part, index=False)
            output = root / "signals.parquet"
            original = pd.DataFrame({"sentinel": [42]})
            original.to_parquet(output, index=False)

            with self.assertRaisesRegex(ValueError, "_manifest"):
                generate_signals([part], output)

            pd.testing.assert_frame_equal(pd.read_parquet(output), original)

    def test_signal_reports_change_without_claiming_alert_severity(self):
        snapshot_at = pd.Timestamp(
            "2026-07-17 18:00:00",
            tz="Asia/Ho_Chi_Minh",
        )
        frame = pd.DataFrame(
            {
                "river_point_id": ["nam_rom_01"] * 4,
                "river_name": ["Nậm Rốm"] * 4,
                "point_name": ["Nậm Rốm 01"] * 4,
                "snapshot_at": [snapshot_at] * 4,
                "valid_date": pd.to_datetime(
                    ["2026-07-17", "2026-07-18", "2026-07-19", "2026-07-20"]
                ).date,
                "river_discharge": [10.0, 12.0, 14.0, 16.0],
                "river_discharge_p25": [9.0, 10.0, 12.0, 11.0],
                "river_discharge_p75": [11.0, 14.0, 20.0, 18.0],
                "grid_latitude": [21.325] * 4,
                "grid_longitude": [103.025] * 4,
                "model": ["glofas_v4_seamless"] * 4,
            }
        )

        result = build_flood_signals(frame)

        self.assertEqual(len(result), 1)
        row = result.iloc[0]
        self.assertEqual(row["trend_signal"], "rising")
        self.assertAlmostEqual(row["peak_change_percent"], 60.0)
        self.assertEqual(row["peak_valid_date"], pd.Timestamp("2026-07-20").date())
        self.assertNotIn("severity", result.columns)
        self.assertFalse(bool(row["is_official_warning"]))
        self.assertTrue(bool(row["is_representative_grid_cell"]))

    def test_signal_handles_zero_baseline_without_infinite_ratio(self):
        snapshot_at = pd.Timestamp(
            "2026-07-17 18:00:00",
            tz="Asia/Ho_Chi_Minh",
        )
        frame = pd.DataFrame(
            {
                "river_point_id": ["nam_muc_01", "nam_muc_01"],
                "river_name": ["Nậm Mức", "Nậm Mức"],
                "point_name": ["Nậm Mức 01", "Nậm Mức 01"],
                "snapshot_at": [snapshot_at, snapshot_at],
                "valid_date": pd.to_datetime(
                    ["2026-07-17", "2026-07-18"]
                ).date,
                "river_discharge": [0.0, 2.0],
                "river_discharge_p25": [0.0, 1.0],
                "river_discharge_p75": [0.0, 3.0],
                "grid_latitude": [21.975] * 2,
                "grid_longitude": [103.275] * 2,
                "model": ["glofas_v4_seamless", "glofas_v4_seamless"],
            }
        )

        result = build_flood_signals(frame)

        self.assertTrue(pd.isna(result.iloc[0]["peak_change_percent"]))
        self.assertEqual(result.iloc[0]["trend_signal"], "baseline_unavailable")

    def test_monotonically_falling_series_is_classified_as_falling(self):
        snapshot_at = pd.Timestamp(
            "2026-07-17 18:00:00",
            tz="Asia/Ho_Chi_Minh",
        )
        frame = pd.DataFrame(
            {
                "river_point_id": ["x"] * 3,
                "river_name": ["Sông X"] * 3,
                "point_name": ["X 01"] * 3,
                "snapshot_at": [snapshot_at] * 3,
                "valid_date": pd.to_datetime(
                    ["2026-07-17", "2026-07-18", "2026-07-19"]
                ).date,
                "river_discharge": [10.0, 8.0, 6.0],
                "river_discharge_p25": [9.0, 7.0, 5.0],
                "river_discharge_p75": [11.0, 9.0, 7.0],
                "grid_latitude": [21.325] * 3,
                "grid_longitude": [103.025] * 3,
                "model": ["glofas_v4_seamless"] * 3,
            }
        )

        result = build_flood_signals(frame)

        self.assertEqual(result.iloc[0]["trend_signal"], "falling")
        self.assertAlmostEqual(result.iloc[0]["horizon_change_percent"], -40.0)

    def test_duplicate_point_date_is_rejected(self):
        snapshot_at = pd.Timestamp(
            "2026-07-17 18:00:00",
            tz="Asia/Ho_Chi_Minh",
        )
        frame = pd.DataFrame(
            {
                "river_point_id": ["x", "x"],
                "river_name": ["Sông X", "Sông X"],
                "point_name": ["X", "X"],
                "snapshot_at": [snapshot_at, snapshot_at],
                "valid_date": [pd.Timestamp("2026-07-17").date()] * 2,
                "river_discharge": [1.0, 2.0],
                "river_discharge_p25": [0.5, 1.0],
                "river_discharge_p75": [1.5, 3.0],
                "grid_latitude": [21.325, 21.325],
                "grid_longitude": [103.025, 103.025],
                "model": ["glofas_v4_seamless"] * 2,
            }
        )

        with self.assertRaisesRegex(ValueError, "trùng"):
            build_flood_signals(frame)


if __name__ == "__main__":
    unittest.main()
