import unittest
from pathlib import Path

import pandas as pd

from data.download_historical_weather import (
    HOURLY_VARIABLES,
    estimate_rows,
    response_to_frame,
    write_batch,
)


class HistoricalWeatherPipelineTest(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
