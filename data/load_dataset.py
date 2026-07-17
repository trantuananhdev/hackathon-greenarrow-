from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


DATA_ROOT = Path(__file__).resolve().parent


def locate_dataset(name: str | Path) -> Path | None:
    """Resolve a dataset artifact by name from the data directory."""
    path = Path(name)
    if path.is_absolute():
        return path if path.exists() else None
    if path.exists():
        return path.resolve()

    candidates = [
        Path.cwd() / path,
        DATA_ROOT / path,
        DATA_ROOT / path.name,
        DATA_ROOT / path.stem,
    ]
    for candidate in candidates:
        if candidate.exists() and candidate.is_file():
            return candidate.resolve()

    for discovered in sorted(DATA_ROOT.glob("**/*")):
        if discovered.is_file() and discovered.name == path.name:
            return discovered.resolve()
    return None


def load_dataset(name: str | Path) -> tuple[pd.DataFrame, dict[str, Any] | None]:
    """Load a parquet dataset and its companion manifest if present."""
    dataset_path = locate_dataset(name)
    if dataset_path is None:
        raise FileNotFoundError(f"No dataset found for {name}")

    frame = pd.read_parquet(dataset_path)
    manifest: dict[str, Any] | None = None
    for manifest_path in (
        dataset_path.with_suffix(".manifest.json"),
        dataset_path.with_name(dataset_path.stem + ".manifest.json"),
    ):
        if manifest_path.exists():
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            break
    return frame, manifest


if __name__ == "__main__":
    frame, manifest = load_dataset("dien_bien_locations.parquet")
    print(f"Loaded {len(frame)} rows from {Path('dien_bien_locations.parquet')}")
    if manifest is not None:
        print(json.dumps(manifest, ensure_ascii=False, indent=2))
