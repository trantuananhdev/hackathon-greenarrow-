"""Normalize DesInventar disaster records into training-eligible events."""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
import uuid
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Iterable, Iterator, Mapping

import pandas as pd

TIMEZONE = "Asia/Ho_Chi_Minh"
RECORD_TAGS = {"tr", "ficha", "record", "row"}

ALIASES = {
    "raw_uuid": ("uu_id", "uuid", "guid"),
    "raw_serial": ("serial", "id", "evento_id"),
    "raw_hazard": ("evento", "event", "hazard", "type"),
    "raw_admin_unit": ("lugar", "place", "location", "name1", "level1_name"),
    "raw_province": ("level0", "province", "name0", "level0_name"),
    "raw_year": ("fechano", "year", "anio"),
    "raw_month": ("fechames", "month", "mes"),
    "raw_day": ("fechadia", "day", "dia"),
    "raw_date": ("fecha", "date", "event_date"),
    "raw_source": ("fuente", "fuentes", "source", "sources"),
    "deaths": ("muertos", "deaths", "dead"),
    "injured": ("heridos", "injured"),
    "missing": ("desaparece", "missing"),
    "affected": ("afectados", "affected"),
    "evacuated": ("evacuados", "evacuated"),
    "houses_destroyed": ("vivdest", "houses_destroyed"),
    "houses_damaged": ("vivafec", "houses_damaged"),
}
ALIAS_LOOKUP = {
    alias: destination for destination, aliases in ALIASES.items() for alias in aliases
}

EVENT_COLUMNS = [
    "event_id",
    "event_date",
    "hazard",
    "province",
    "spatial_precision",
    "source_name",
    "source_record_id",
    "source_url",
    "old_admin_unit",
    "new_admin_unit",
    "location_id",
    "admin_match_status",
    "deaths",
    "injured",
    "missing",
    "affected",
    "evacuated",
    "houses_destroyed",
    "houses_damaged",
    "raw_uuid",
    "raw_serial",
    "raw_hazard",
    "raw_admin_unit",
    "raw_province",
    "raw_date",
    "raw_year",
    "raw_month",
    "raw_day",
    "raw_source",
    "source_sha256",
    "retrieved_at",
]
IMPACT_COLUMNS = [
    "deaths",
    "injured",
    "missing",
    "affected",
    "evacuated",
    "houses_destroyed",
    "houses_damaged",
]


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1].casefold()


def parse_desinventar_xml(path: Path) -> Iterator[dict[str, str | None]]:
    """Stream records from a DesInventar XML export without loading the tree."""
    inside_records = False
    for action, element in ET.iterparse(path, events=("start", "end")):
        tag = local_name(element.tag)
        if action == "start" and tag == "fichas":
            inside_records = True
            continue
        if action == "end" and tag == "fichas":
            inside_records = False
            element.clear()
            continue
        if action != "end" or not inside_records or tag not in RECORD_TAGS:
            continue
        values: dict[str, str | None] = {key: None for key in ALIASES}
        for child in element:
            destination = ALIAS_LOOKUP.get(local_name(child.tag))
            if destination:
                text = "".join(child.itertext()).strip()
                values[destination] = text or None
        # Ignore structural rows that have no event identity/content.
        if any(values.get(key) for key in ("raw_serial", "raw_uuid", "raw_hazard")):
            yield values
        element.clear()


def _ascii(value: object) -> str:
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = text.replace("Đ", "D").replace("đ", "d")
    return "".join(char for char in text if not unicodedata.combining(char))


def canonical_text(value: object) -> str:
    return re.sub(r"\s+", " ", _ascii(value).casefold()).strip()


def canonical_admin(value: object) -> str:
    text = canonical_text(value)
    return re.sub(
        r"^(xa|phuong|thi tran|huyen|quan|thanh pho|tp)\s+",
        "",
        text,
    )


def _parse_date(row: Mapping[str, object]) -> pd.Timestamp | None:
    raw_date = row.get("raw_date")
    if raw_date:
        parsed = pd.to_datetime(raw_date, errors="coerce", dayfirst=True)
        if not pd.isna(parsed):
            return pd.Timestamp(parsed).normalize().tz_localize(None)
    pieces = [row.get("raw_year"), row.get("raw_month"), row.get("raw_day")]
    if not all(value not in (None, "") for value in pieces):
        return None
    try:
        return pd.Timestamp(
            year=int(str(pieces[0])),
            month=int(str(pieces[1])),
            day=int(str(pieces[2])),
        )
    except (TypeError, ValueError):
        return None


def _nullable_integer(value: object) -> int | pd._libs.missing.NAType:
    if value in (None, ""):
        return pd.NA
    numeric = pd.to_numeric(value, errors="coerce")
    if pd.isna(numeric) or float(numeric) < 0:
        return pd.NA
    return int(float(numeric))


def normalize_hazard(value: object) -> str:
    text = canonical_text(value)
    aliases = {
        "flood": "flood",
        "inundacion": "flood",
        "lu": "flood",
        "flash flood": "flash_flood",
        "lu quet": "flash_flood",
        "landslide": "landslide",
        "deslizamiento": "landslide",
        "sat lo": "landslide",
        "storm": "storm",
        "tempestad": "storm",
        "bao": "storm",
        "cold wave": "cold_wave",
        "frost": "frost",
        "hail": "hail",
        "hailstorm": "hail",
        "loc+ mua da": "hail",
        "loc mua da": "hail",
    }
    return aliases.get(text, text.replace(" ", "_") or "unknown")


def _event_id(row: Mapping[str, object]) -> str:
    candidate = str(row.get("raw_uuid") or "").strip()
    try:
        return f"desinventar-vnm-{uuid.UUID(candidate)}"
    except (ValueError, AttributeError):
        identity = {
            key: canonical_text(row.get(key))
            for key in (
                "raw_serial",
                "raw_hazard",
                "raw_admin_unit",
                "raw_province",
                "raw_date",
                "raw_year",
                "raw_month",
                "raw_day",
            )
        }
        digest = hashlib.sha256(
            json.dumps(identity, sort_keys=True, ensure_ascii=False).encode("utf-8")
        ).hexdigest()
        return f"desinventar-vnm-sha256-{digest}"


def _admin_lookup(
    locations: pd.DataFrame,
) -> tuple[dict[str, dict[str, object]], dict[str, str]]:
    required = {"location_id", "province", "old_admin_unit", "new_admin_unit"}
    if missing := required.difference(locations.columns):
        raise ValueError(f"Missing location columns: {sorted(missing)}")
    old_lookup: dict[str, dict[str, object]] = {}
    new_lookup: dict[str, str] = {}
    for row in locations.to_dict("records"):
        old_lookup.setdefault(canonical_admin(row["old_admin_unit"]), row)
        new_lookup.setdefault(
            canonical_admin(row["new_admin_unit"]), str(row["new_admin_unit"])
        )
    return old_lookup, new_lookup


def _empty_frame(columns: list[str]) -> pd.DataFrame:
    frame = pd.DataFrame(columns=columns)
    for column in IMPACT_COLUMNS:
        if column in frame:
            frame[column] = frame[column].astype("Int64")
    return frame


def build_event_inventory(
    rows: Iterable[Mapping[str, object]],
    locations: pd.DataFrame,
    source_sha256: str,
    source_url: str = "https://www.desinventar.net",
    retrieved_at: pd.Timestamp | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return eligible Điện Biên events and a quarantine with explicit reasons."""
    retrieved = retrieved_at or pd.Timestamp.now(tz=TIMEZONE)
    retrieved = pd.Timestamp(retrieved)
    if retrieved.tzinfo is None:
        retrieved = retrieved.tz_localize(TIMEZONE)
    else:
        retrieved = retrieved.tz_convert(TIMEZONE)
    old_lookup, new_lookup = _admin_lookup(locations)
    accepted: list[dict[str, object]] = []
    rejected: list[dict[str, object]] = []
    for source_row in rows:
        row = {key: source_row.get(key) for key in ALIASES}
        event_date = _parse_date(row)
        province_is_dien_bien = canonical_text(row["raw_province"]) == "dien bien"
        reason = None
        if not province_is_dien_bien:
            reason = "outside_dien_bien"
        elif event_date is None:
            reason = "incomplete_or_invalid_date"
        admin_key = canonical_admin(row["raw_admin_unit"])
        old_match = old_lookup.get(admin_key)
        new_match = new_lookup.get(admin_key)
        match_status = (
            "exact_old" if old_match else "exact_new" if new_match else "unmatched"
        )
        record = {
            "event_id": _event_id(row),
            "event_date": event_date,
            "hazard": normalize_hazard(row["raw_hazard"]),
            "province": "Điện Biên" if province_is_dien_bien else row["raw_province"],
            "spatial_precision": "province",
            "source_name": "DesInventar Sendai",
            "source_record_id": row["raw_uuid"] or row["raw_serial"],
            "source_url": source_url,
            "old_admin_unit": old_match["old_admin_unit"] if old_match else pd.NA,
            "new_admin_unit": (
                old_match["new_admin_unit"] if old_match else new_match or pd.NA
            ),
            "location_id": old_match["location_id"] if old_match else pd.NA,
            "admin_match_status": match_status,
            **{column: _nullable_integer(row.get(column)) for column in IMPACT_COLUMNS},
            **{key: row.get(key) for key in ALIASES if key not in IMPACT_COLUMNS},
            "source_sha256": source_sha256,
            "retrieved_at": retrieved,
        }
        if reason:
            rejected.append({**record, "rejection_reason": reason})
        else:
            accepted.append(record)
    frame = pd.DataFrame(accepted, columns=EVENT_COLUMNS)
    quarantine = pd.DataFrame(rejected, columns=EVENT_COLUMNS + ["rejection_reason"])
    if frame.empty:
        frame = _empty_frame(EVENT_COLUMNS)
    if quarantine.empty:
        quarantine = _empty_frame(EVENT_COLUMNS + ["rejection_reason"])
    for target in (frame, quarantine):
        for column in IMPACT_COLUMNS:
            target[column] = pd.array(target[column], dtype="Int64")
        if not target.empty:
            target["event_date"] = pd.to_datetime(target["event_date"])
            target["retrieved_at"] = pd.to_datetime(target["retrieved_at"])
    if not frame.empty and frame["event_id"].duplicated().any():
        raise ValueError("Duplicate normalized event_id")
    return frame, quarantine
