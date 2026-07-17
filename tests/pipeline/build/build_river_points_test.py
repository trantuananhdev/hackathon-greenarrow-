import json
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from pipeline.build.build_river_points import (
    RIVER_WAYS,
    build_river_points,
    payload_sha256,
    write_river_points,
)


def make_way_payload(way_id: int, node_count: int = 11) -> dict:
    node_ids = list(range(1_000, 1_000 + node_count))
    elements = [
        {
            "type": "node",
            "id": node_id,
            "lat": 21.0 + index * 0.01,
            "lon": 103.0 + index * 0.02,
        }
        for index, node_id in enumerate(node_ids)
    ]
    elements.append(
        {
            "type": "way",
            "id": way_id,
            "nodes": node_ids,
            "tags": {"name": "Sông thử nghiệm", "waterway": "river"},
        }
    )
    return {"version": "0.6", "generator": "test", "elements": elements}


class RiverPointBuilderTest(unittest.TestCase):
    def test_selects_four_deterministic_interior_nodes_in_way_order(self):
        way_id = 279788696
        payload = make_way_payload(way_id)
        retrieved_at = pd.Timestamp(
            "2026-07-17 19:00:00",
            tz="Asia/Ho_Chi_Minh",
        )

        first = build_river_points(
            {way_id: payload},
            {way_id: "Nậm Rốm"},
            retrieved_at,
        )
        second = build_river_points(
            {way_id: payload},
            {way_id: "Nậm Rốm"},
            retrieved_at,
        )

        self.assertEqual(len(first), 4)
        self.assertEqual(first["osm_node_id"].tolist(), [1002, 1004, 1006, 1008])
        self.assertEqual(first["river_point_id"].tolist(), second["river_point_id"].tolist())
        self.assertEqual(
            first["river_point_id"].tolist(),
            [
                "osm-way-279788696-node-1002",
                "osm-way-279788696-node-1004",
                "osm-way-279788696-node-1006",
                "osm-way-279788696-node-1008",
            ],
        )
        node_coordinates = {
            (element["id"], element["lat"], element["lon"])
            for element in payload["elements"]
            if element["type"] == "node"
        }
        self.assertTrue(
            all(
                (row.osm_node_id, row.latitude, row.longitude)
                in node_coordinates
                for row in first.itertuples()
            )
        )
        self.assertTrue(first["distance_fraction"].is_monotonic_increasing)
        self.assertEqual(first["source"].unique().tolist(), ["OpenStreetMap"])
        self.assertEqual(
            first["source_attribution"].unique().tolist(),
            ["© OpenStreetMap contributors"],
        )
        self.assertEqual(
            first["point_name"].tolist(),
            ["Nậm Rốm 01", "Nậm Rốm 02", "Nậm Rốm 03", "Nậm Rốm 04"],
        )
        self.assertEqual(
            first["source_url"].unique().tolist(),
            ["https://api.openstreetmap.org/api/0.6/way/279788696/full.json"],
        )

    def test_rejects_way_without_enough_interior_nodes(self):
        way_id = 67504081
        with self.assertRaisesRegex(ValueError, "interior"):
            build_river_points(
                {way_id: make_way_payload(way_id, node_count=5)},
                {way_id: "Nậm Mức"},
                pd.Timestamp.now(tz="Asia/Ho_Chi_Minh"),
            )

    def test_atomic_output_manifest_contains_source_fingerprints(self):
        retrieved_at = pd.Timestamp(
            "2026-07-17 19:00:00",
            tz="Asia/Ho_Chi_Minh",
        )
        payloads = {
            way_id: make_way_payload(way_id)
            for way_id in RIVER_WAYS
        }
        frame = build_river_points(
            payloads,
            RIVER_WAYS,
            retrieved_at,
        )

        with tempfile.TemporaryDirectory() as temporary_directory:
            output = Path(temporary_directory) / "river_points.parquet"
            write_river_points(frame, output, payloads)

            written = pd.read_parquet(output)
            manifest = json.loads(
                output.with_suffix(".manifest.json").read_text(encoding="utf-8")
            )

        self.assertEqual(len(written), 12)
        self.assertEqual(manifest["points"], 12)
        self.assertEqual(manifest["ways"], 3)
        self.assertEqual(manifest["license"], "ODbL 1.0")
        self.assertEqual(
            manifest["source_sha256_by_way"]["279788696"],
            payload_sha256(payloads[279788696]),
        )
        self.assertEqual(len(manifest["source_fingerprint_sha256"]), 64)


if __name__ == "__main__":
    unittest.main()
