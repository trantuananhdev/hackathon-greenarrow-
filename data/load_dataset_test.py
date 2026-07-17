import unittest

from data.load_dataset import locate_dataset, load_dataset
# from load_dataset import locate_dataset, load_dataset


class LoadDatasetTest(unittest.TestCase):
    def test_locate_existing_dataset(self) -> None:
        path = locate_dataset("dien_bien_locations.parquet")
        self.assertTrue(path is not None)
        self.assertTrue(path.exists())
        self.assertEqual(path.name, "dien_bien_locations.parquet")

    def test_load_dataset_returns_frame_and_optional_manifest(self) -> None:
        frame, manifest = load_dataset("dien_bien_locations.parquet")
        self.assertFalse(frame.empty)
        self.assertIn("location_id", frame.columns)
        self.assertIn("province", frame.columns)
        self.assertTrue(manifest is None or isinstance(manifest, dict))


if __name__ == "__main__":
    unittest.main()
