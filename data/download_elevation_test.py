import unittest

import pandas as pd

from data.download_elevation import build_location_features


class ElevationPipelineTest(unittest.TestCase):
    def test_api_elevations_map_to_location_ids_without_admin_columns(self):
        locations = pd.DataFrame(
            {
                "location_id": [10, 20],
                "old_admin_unit": ["Xã cũ A", "Xã cũ B"],
                "new_admin_unit": ["Xã mới", "Xã mới"],
                "latitude": [21.1, 21.2],
                "longitude": [103.1, 103.2],
            }
        )
        retrieved_at = pd.Timestamp(
            "2026-07-17 11:00:00",
            tz="Asia/Ho_Chi_Minh",
        )

        features = build_location_features(
            locations,
            {"elevation": [500.0, 900.0]},
            retrieved_at,
        )

        self.assertEqual(features["location_id"].tolist(), [10, 20])
        self.assertEqual(features["elevation_m"].tolist(), [500.0, 900.0])
        self.assertEqual(
            features["elevation_source"].unique().tolist(),
            ["copernicus_dem_90m"],
        )
        self.assertNotIn("old_admin_unit", features.columns)
        self.assertNotIn("new_admin_unit", features.columns)
        self.assertEqual(
            str(features["elevation_retrieved_at"].dt.tz),
            "Asia/Ho_Chi_Minh",
        )


if __name__ == "__main__":
    unittest.main()
