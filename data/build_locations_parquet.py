import hashlib
import sys
from pathlib import Path

import pandas as pd

from location_source import parse_rows


def stable_location_id(
    old_admin_unit: str,
    latitude: float,
    longitude: float,
) -> int:
    key = f"{old_admin_unit}|{latitude:.4f}|{longitude:.4f}".encode("utf-8")
    return int.from_bytes(hashlib.sha256(key).digest()[:7], "big")


def build_parquet(source_path: Path, parquet_path: Path) -> int:
    rows = parse_rows(source_path)
    if len(rows) != 85:
        raise ValueError(
            f"Cần đúng 85 địa danh từ {source_path}, đọc được {len(rows)}"
        )

    frame = pd.DataFrame(
        rows,
        columns=[
            "old_admin_unit",
            "new_admin_unit",
            "latitude",
            "longitude",
        ],
    )
    if frame[["old_admin_unit", "new_admin_unit"]].isna().any().any():
        raise ValueError("Tên đơn vị hành chính không được rỗng")
    if not frame["latitude"].between(20.8, 22.6).all():
        raise ValueError("Có latitude nằm ngoài phạm vi Điện Biên")
    if not frame["longitude"].between(101.8, 103.8).all():
        raise ValueError("Có longitude nằm ngoài phạm vi Điện Biên")
    if frame.duplicated(["old_admin_unit", "latitude", "longitude"]).any():
        raise ValueError("Có địa danh/tọa độ trùng")

    frame.insert(
        0,
        "location_id",
        [
            stable_location_id(old_name, latitude, longitude)
            for old_name, _, latitude, longitude in rows
        ],
    )
    if not frame["location_id"].is_unique:
        raise ValueError("Hash location_id bị trùng")
    frame.insert(1, "province", "Điện Biên")
    frame["coordinate_reference"] = (
        "Điểm trung tâm đơn vị hành chính cũ, làm tròn 4 chữ số"
    )

    parquet_path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_parquet(
        parquet_path,
        index=False,
        engine="pyarrow",
        compression="zstd",
    )
    return len(frame)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(
            "Cách dùng: python data/build_locations_parquet.py "
            "<pasted-text.txt> <locations.parquet>"
        )
    count = build_parquet(Path(sys.argv[1]), Path(sys.argv[2]))
    print(f"Đã ghi {count} địa danh vào {sys.argv[2]}")
