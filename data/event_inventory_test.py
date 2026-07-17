import hashlib
import json
import unittest
import zipfile
from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd

from data.download_desinventar import materialize_desinventar
from data.event_inventory import build_event_inventory, parse_desinventar_xml


XML = """<?xml version="1.0" encoding="UTF-8"?>
<DESINVENTAR>
<eventos><TR><serial>99</serial><evento>STRUCTURAL</evento></TR></eventos>
<fichas>
  <TR><uu_id>550e8400-e29b-41d4-a716-446655440000</uu_id>
    <serial>DB-1</serial><evento>FLOOD</evento><lugar>Noong Bua</lugar>
    <level0>DIEN BIEN</level0><fechano>2024</fechano><fechames>8</fechames>
    <fechadia>11</fechadia><muertos>2</muertos><afectados></afectados>
    <fuente>Provincial report</fuente></TR>
  <TR><serial>DB-2</serial><evento>LANDSLIDE</evento><lugar>Unknown place</lugar>
    <level0>Điện Biên</level0><fechano>2023</fechano><fechames>7</fechames>
    <fuente>Archive</fuente></TR>
  <TR><serial>SL-1</serial><evento>FLOOD</evento><lugar>Other</lugar>
    <level0>Sơn La</level0><fechano>2024</fechano><fechames>8</fechames>
    <fechadia>11</fechadia></TR>
</fichas></DESINVENTAR>""".encode("utf-8")


class EventInventoryTest(unittest.TestCase):
    def locations(self):
        return pd.DataFrame(
            {
                "location_id": ["old-noong-bua"],
                "province": ["Điện Biên"],
                "old_admin_unit": ["Phường Noong Bua"],
                "new_admin_unit": ["Phường Mường Thanh"],
                "latitude": [21.4],
                "longitude": [103.0],
            }
        )

    def test_stream_parser_preserves_raw_fields(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "events.xml"
            path.write_bytes(XML)
            rows = list(parse_desinventar_xml(path))
        self.assertEqual(len(rows), 3)
        self.assertEqual(rows[0]["raw_hazard"], "FLOOD")
        self.assertEqual(rows[0]["raw_admin_unit"], "Noong Bua")
        self.assertEqual(rows[0]["raw_source"], "Provincial report")

    def test_inventory_filters_province_and_quarantines_incomplete_date(self):
        frame, rejected = build_event_inventory(
            list(parse_desinventar_xml_bytes(XML)),
            self.locations(),
            source_sha256="a" * 64,
            retrieved_at=pd.Timestamp("2026-07-17T20:00:00+07:00"),
        )
        self.assertEqual(len(frame), 1)
        event = frame.iloc[0]
        self.assertEqual(event["event_id"], "desinventar-vnm-550e8400-e29b-41d4-a716-446655440000")
        self.assertEqual(event["admin_match_status"], "exact_old")
        self.assertEqual(event["old_admin_unit"], "Phường Noong Bua")
        self.assertEqual(event["new_admin_unit"], "Phường Mường Thanh")
        self.assertEqual(event["event_date"], pd.Timestamp("2024-08-11"))
        self.assertEqual(event["deaths"], 2)
        self.assertTrue(pd.isna(event["affected"]))
        self.assertEqual(set(rejected["rejection_reason"]), {
            "incomplete_or_invalid_date",
            "outside_dien_bien",
        })

    def test_hash_identity_is_stable_without_uuid(self):
        rows = list(parse_desinventar_xml_bytes(XML))
        rows[1]["raw_day"] = "12"
        first, _ = build_event_inventory(rows[1:2], self.locations(), "b" * 64)
        rows[1]["raw_source"] = "A later source citation"
        second, _ = build_event_inventory(rows[1:2], self.locations(), "b" * 64)
        self.assertRegex(first.iloc[0]["event_id"], r"^desinventar-vnm-sha256-[0-9a-f]{64}$")
        self.assertEqual(first.iloc[0]["event_id"], second.iloc[0]["event_id"])
        self.assertEqual(first.iloc[0]["admin_match_status"], "unmatched")

    def test_materialize_zip_is_atomic_and_manifest_binds_hash(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            archive = root / "source.zip"
            with zipfile.ZipFile(archive, "w") as bundle:
                bundle.writestr("catalog/events.xml", XML)
            digest = hashlib.sha256(archive.read_bytes()).hexdigest()
            locations_path = root / "locations.parquet"
            self.locations().to_parquet(locations_path, index=False)
            output = root / "events.parquet"
            materialize_desinventar(
                archive,
                locations_path,
                output,
                source_url="https://example.test/events.zip",
                expected_sha256=digest,
            )
            manifest = json.loads(
                output.with_suffix(".manifest.json").read_text(encoding="utf-8")
            )
            self.assertEqual(manifest["source_sha256"], digest)
            self.assertEqual(manifest["accepted_rows"], 1)
            self.assertTrue(output.exists())
            self.assertTrue(output.with_name("events.rejected.parquet").exists())
            self.assertFalse(list(root.glob("*.tmp")))

    def test_materialize_rejects_unverified_source(self):
        with TemporaryDirectory() as directory:
            source = Path(directory) / "events.xml"
            source.write_bytes(XML)
            locations = Path(directory) / "locations.parquet"
            self.locations().to_parquet(locations, index=False)
            with self.assertRaisesRegex(ValueError, "SHA-256"):
                materialize_desinventar(
                    source,
                    locations,
                    Path(directory) / "output.parquet",
                    source_url="https://example.test/events.xml",
                    expected_sha256="0" * 64,
                )


def parse_desinventar_xml_bytes(content):
    with TemporaryDirectory() as directory:
        path = Path(directory) / "events.xml"
        path.write_bytes(content)
        return list(parse_desinventar_xml(path))


if __name__ == "__main__":
    unittest.main()
