import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd

from data.download_event_weather import (
    HOURLY_VARIABLES,
    MODEL,
    TIMEZONE,
    download_event_weather,
    event_window,
    responses_to_frame,
    validate_configuration,
    validate_event_part,
)


def locations_frame(count: int = 2) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "location_id": range(1, count + 1),
            "latitude": [21.4 + index * 0.01 for index in range(count)],
            "longitude": [103.0 + index * 0.01 for index in range(count)],
        }
    )


def event_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "event_id": ["evt-001"],
            "event_date": ["2024-08-10"],
            "spatial_precision": ["province"],
            "source_name": ["DesInventar"],
            "source_record_id": ["original-1"],
            "source_url": ["https://example.test/events/1"],
            "record_eligible_for_era5": [True],
        }
    )


def api_response(latitude: float, longitude: float) -> dict:
    times = pd.date_range(
        "2024-08-07 00:00",
        "2024-08-12 23:00",
        freq="h",
    )
    hourly = {"time": times.strftime("%Y-%m-%dT%H:%M").tolist()}
    hourly.update({name: [1.0] * len(times) for name in HOURLY_VARIABLES})
    return {
        "latitude": latitude,
        "longitude": longitude,
        "elevation": 500.0,
        "timezone": TIMEZONE,
        "hourly": hourly,
    }


class EventWeatherTest(unittest.TestCase):
    def test_invalid_dry_run_configuration_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "batch_size"):
            validate_configuration(0, 0, 72, 48)
        with self.assertRaisesRegex(ValueError, "Batch/window"):
            validate_configuration(10, 0, -1, 48)

    def test_window_is_exact_and_training_eligibility_precedes_event(self):
        start, event_at, end = event_window("2024-08-10", 72, 48)
        self.assertEqual(start.isoformat(), "2024-08-07T00:00:00+07:00")
        self.assertEqual(end.isoformat(), "2024-08-12T00:00:00+07:00")

        locations = locations_frame()
        responses = [
            api_response(row.latitude, row.longitude)
            for row in locations.itertuples()
        ]
        frame = responses_to_frame(
            event_frame().iloc[0].to_dict(),
            locations,
            responses,
            start,
            event_at,
            end,
            pd.Timestamp("2026-07-17 12:00", tz=TIMEZONE),
        )

        self.assertEqual(len(frame), 2 * 121)
        self.assertEqual(frame.groupby("location_id")["time"].nunique().tolist(), [121, 121])
        self.assertTrue((frame.loc[frame["training_feature_eligible"], "time"] < event_at).all())
        self.assertFalse(frame.loc[frame["time"] >= event_at, "training_feature_eligible"].any())
        self.assertEqual(set(frame["spatial_precision"]), {"province"})

    def test_validation_rejects_broken_hourly_cadence(self):
        locations = locations_frame(1)
        start, event_at, end = event_window("2024-08-10", 72, 48)
        frame = responses_to_frame(
            event_frame().iloc[0].to_dict(),
            locations,
            [api_response(21.4, 103.0)],
            start,
            event_at,
            end,
            pd.Timestamp("2026-07-17 12:00", tz=TIMEZONE),
        ).drop(index=10)
        with self.assertRaisesRegex(ValueError, "121"):
            validate_event_part(
                frame,
                "evt-001",
                locations,
                start,
                event_at,
                end,
                "province",
            )

    def test_validation_rejects_distant_grid_and_null_weather(self):
        locations = locations_frame(1)
        start, event_at, end = event_window("2024-08-10", 72, 48)
        response = api_response(23.0, 105.0)
        response["hourly"][HOURLY_VARIABLES[0]] = [None] * 144
        with self.assertRaisesRegex(ValueError, "rỗng|Grid"):
            responses_to_frame(
                event_frame().iloc[0].to_dict(),
                locations,
                [response],
                start,
                event_at,
                end,
                pd.Timestamp("2026-07-17 12:00", tz=TIMEZONE),
            )

    @patch("data.download_event_weather.time.sleep")
    @patch("data.download_event_weather.fetch_batch")
    def test_resume_and_manifest_lineage(self, fetch_batch, _sleep):
        fetch_batch.side_effect = lambda _session, batch, _start, _end: [
            api_response(row.latitude, row.longitude)
            for row in batch.itertuples()
        ]
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            events_path = root / "events.parquet"
            locations_path = root / "locations.parquet"
            output = root / "weather"
            event_frame().to_parquet(events_path, index=False)
            locations_frame().to_parquet(locations_path, index=False)

            result = download_event_weather(
                events_path,
                locations_path,
                output,
                batch_size=1,
                request_delay=0,
            )
            self.assertEqual(result, (2, 0))
            event_dir = output / "event_id=evt-001"
            self.assertTrue((event_dir / "_SUCCESS").exists())
            manifest = json.loads((event_dir / "_manifest.json").read_text(encoding="utf-8"))
            self.assertIn("events_sha256", manifest)
            self.assertIn("locations_sha256", manifest)
            self.assertEqual(manifest["event_provenance"]["source_record_id"], "original-1")

            fetch_batch.reset_mock()
            self.assertEqual(
                download_event_weather(
                    events_path,
                    locations_path,
                    output,
                    batch_size=1,
                    request_delay=0,
                ),
                (0, 2),
            )
            fetch_batch.assert_not_called()

    def test_rejects_duplicate_or_unsafe_event_ids(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            events_path = root / "events.parquet"
            locations_path = root / "locations.parquet"
            locations_frame().to_parquet(locations_path, index=False)
            duplicated = pd.concat([event_frame(), event_frame()], ignore_index=True)
            duplicated.to_parquet(events_path, index=False)
            with self.assertRaisesRegex(ValueError, "event_id"):
                download_event_weather(events_path, locations_path, root / "out", request_delay=0)

            unsafe = event_frame()
            unsafe.loc[0, "event_id"] = "../escape"
            unsafe.to_parquet(events_path, index=False)
            with self.assertRaisesRegex(ValueError, "event_id"):
                download_event_weather(events_path, locations_path, root / "out2", request_delay=0)


if __name__ == "__main__":
    unittest.main()
