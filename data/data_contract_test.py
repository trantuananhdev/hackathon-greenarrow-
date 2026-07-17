import unittest

import pandas as pd

from data.data_contract import validate_forecast_output


class ForecastDataContractTest(unittest.TestCase):
    def make_valid_frame(self):
        snapshot_at = pd.Timestamp(
            "2026-07-17 10:30:00",
            tz="Asia/Ho_Chi_Minh",
        )
        return pd.DataFrame(
            {
                "location_id": [1, 1],
                "snapshot_at": [snapshot_at, snapshot_at],
                "valid_time": pd.DatetimeIndex(
                    [
                        "2026-07-17 11:00:00",
                        "2026-07-17 12:00:00",
                    ],
                    tz="Asia/Ho_Chi_Minh",
                ),
                "model": ["open_meteo_best_match"] * 2,
                "lead_hours": [0.5, 1.5],
                "grid_latitude": [21.0, 21.0],
                "grid_longitude": [103.0, 103.0],
                "grid_elevation": [500.0, 500.0],
                "timezone": ["Asia/Ho_Chi_Minh"] * 2,
                "retrieved_at": [snapshot_at, snapshot_at],
                "temperature_2m": [20.0, 19.5],
                "precipitation": [0.0, 1.0],
                "weather_code": [0, 61],
                "wind_speed_10m": [5.0, 6.0],
                "precipitation_probability": [None, None],
                "wind_gusts_10m": [None, None],
            }
        )

    def test_optional_all_null_variable_warns_without_rejecting_snapshot(self):
        frame = self.make_valid_frame()

        warnings = validate_forecast_output(frame, expected_location_ids={1})

        self.assertEqual(
            warnings,
            [
                "Biến tùy chọn rỗng hoàn toàn: precipitation_probability",
                "Biến tùy chọn rỗng hoàn toàn: wind_gusts_10m",
            ],
        )

    def test_duplicate_forecast_key_is_rejected(self):
        frame = self.make_valid_frame()
        frame.loc[1, "valid_time"] = frame.loc[0, "valid_time"]

        with self.assertRaisesRegex(ValueError, "khóa trùng"):
            validate_forecast_output(frame, expected_location_ids={1})

    def test_missing_location_is_rejected(self):
        frame = self.make_valid_frame()

        with self.assertRaisesRegex(ValueError, "location_id"):
            validate_forecast_output(frame, expected_location_ids={1, 2})

    def test_naive_valid_time_is_rejected(self):
        frame = self.make_valid_frame()
        frame["valid_time"] = frame["valid_time"].dt.tz_localize(None)

        with self.assertRaisesRegex(ValueError, "timezone"):
            validate_forecast_output(frame, expected_location_ids={1})

    def test_incorrect_lead_hours_is_rejected(self):
        frame = self.make_valid_frame()
        frame.loc[0, "lead_hours"] = 99.0

        with self.assertRaisesRegex(ValueError, "lead_hours"):
            validate_forecast_output(frame, expected_location_ids={1})

    def test_required_variable_empty_for_one_location_is_rejected(self):
        frame = pd.concat(
            [
                self.make_valid_frame(),
                self.make_valid_frame().assign(location_id=2),
            ],
            ignore_index=True,
        )
        frame.loc[frame["location_id"] == 2, "precipitation"] = None

        with self.assertRaisesRegex(ValueError, "location_id 2"):
            validate_forecast_output(frame, expected_location_ids={1, 2})


if __name__ == "__main__":
    unittest.main()
