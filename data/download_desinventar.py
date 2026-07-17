"""Download, verify and atomically materialize a DesInventar event inventory."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import urllib.request
import zipfile
from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd

try:
    from data.event_inventory import (
        TIMEZONE,
        build_event_inventory,
        parse_desinventar_xml,
    )
except ModuleNotFoundError:
    from event_inventory import (
        TIMEZONE,
        build_event_inventory,
        parse_desinventar_xml,
    )


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def download_atomic(url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(destination.suffix + ".tmp")
    request = urllib.request.Request(
        url, headers={"User-Agent": "hackathon-greenarrow-data-pipeline/1.0"}
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            with temporary.open("wb") as output:
                shutil.copyfileobj(response, output, length=1024 * 1024)
        temporary.replace(destination)
    finally:
        temporary.unlink(missing_ok=True)


def _xml_from_source(source: Path, work_dir: Path) -> Path:
    if not zipfile.is_zipfile(source):
        return source
    with zipfile.ZipFile(source) as archive:
        members = [
            info for info in archive.infolist()
            if not info.is_dir() and info.filename.casefold().endswith(".xml")
        ]
        if len(members) != 1:
            raise ValueError(
                f"Expected exactly one XML member in ZIP, found {len(members)}"
            )
        output = work_dir / "desinventar.xml"
        with archive.open(members[0]) as zipped, output.open("wb") as extracted:
            shutil.copyfileobj(zipped, extracted, length=1024 * 1024)
        return output


def _write_parquet_atomic(frame: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    try:
        frame.to_parquet(temporary, index=False, compression="zstd")
        pd.read_parquet(temporary)
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def materialize_desinventar(
    raw_source: Path,
    locations_path: Path,
    output_path: Path,
    source_url: str,
    expected_sha256: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    actual_sha256 = file_sha256(raw_source)
    if actual_sha256.casefold() != expected_sha256.casefold():
        raise ValueError(
            f"Source SHA-256 mismatch: expected {expected_sha256}, got {actual_sha256}"
        )
    retrieved_at = pd.Timestamp.now(tz=TIMEZONE)
    locations = pd.read_parquet(locations_path)
    with TemporaryDirectory() as directory:
        xml_path = _xml_from_source(raw_source, Path(directory))
        events, rejected = build_event_inventory(
            parse_desinventar_xml(xml_path),
            locations,
            source_sha256=actual_sha256,
            source_url=source_url,
            retrieved_at=retrieved_at,
        )
    rejected_path = output_path.with_name(
        f"{output_path.stem}.rejected{output_path.suffix}"
    )
    _write_parquet_atomic(events, output_path)
    _write_parquet_atomic(rejected, rejected_path)
    manifest = {
        "dataset": "dien_bien_desinventar_events",
        "source": "DesInventar Sendai",
        "source_url": source_url,
        "source_sha256": actual_sha256,
        "retrieved_at": retrieved_at.isoformat(),
        "locations_sha256": file_sha256(locations_path),
        "accepted_rows": len(events),
        "rejected_rows": len(rejected),
        "eligibility": "Điện Biên province and complete valid event date",
        "admin_matching": "accent-insensitive normalized exact match",
        "rejected_path": rejected_path.name,
    }
    manifest_path = output_path.with_suffix(".manifest.json")
    temporary = manifest_path.with_suffix(".json.tmp")
    try:
        temporary.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        temporary.replace(manifest_path)
    finally:
        temporary.unlink(missing_ok=True)
    return events, rejected


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download and normalize a verified DesInventar export."
    )
    parser.add_argument("--url", required=True)
    parser.add_argument("--sha256", required=True)
    parser.add_argument(
        "--locations", type=Path, default=Path("data/dien_bien_locations.parquet")
    )
    parser.add_argument(
        "--raw", type=Path, default=Path("data/raw/desinventar_export.zip")
    )
    parser.add_argument(
        "--output", type=Path, default=Path("data/desinventar_events.parquet")
    )
    args = parser.parse_args()
    download_atomic(args.url, args.raw)
    events, rejected = materialize_desinventar(
        args.raw, args.locations, args.output, args.url, args.sha256
    )
    print(
        f"Accepted {len(events):,}, rejected {len(rejected):,} -> {args.output}"
    )


if __name__ == "__main__":
    main()
