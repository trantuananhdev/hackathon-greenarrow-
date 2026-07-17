import unittest

import pandas as pd

from pipeline.build.build_event_locations import select_spatial_representatives


class EventLocationSelectionTest(unittest.TestCase):
    def test_selection_is_deterministic_and_spatially_spread(self):
        locations = pd.DataFrame(
            {
                "location_id": [40, 10, 30, 20, 50],
                "latitude": [21.0, 20.0, 22.0, 20.0, 21.0],
                "longitude": [103.0, 102.0, 104.0, 104.0, 102.5],
            }
        )

        first = select_spatial_representatives(locations, count=3)
        second = select_spatial_representatives(locations, count=3)

        self.assertEqual(
            first["location_id"].tolist(),
            second["location_id"].tolist(),
        )
        self.assertEqual(len(first), 3)
        self.assertEqual(first.iloc[0]["location_id"], 10)
        self.assertIn(30, first["location_id"].tolist())
        self.assertEqual(first["selection_method"].nunique(), 1)

    def test_selection_rejects_more_points_than_available(self):
        locations = pd.DataFrame(
            {
                "location_id": [1],
                "latitude": [21.0],
                "longitude": [103.0],
            }
        )
        with self.assertRaisesRegex(ValueError, "count"):
            select_spatial_representatives(locations, count=2)


if __name__ == "__main__":
    unittest.main()
