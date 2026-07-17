import re
from pathlib import Path


ROW_PATTERN = re.compile(
    r"^\|\s*(?P<old_name>[^|]+?)\s*\|"
    r"\s*(?P<latitude>-?\d+(?:\.\d+)?)°\s*N\s*\|"
    r"\s*(?P<longitude>-?\d+(?:\.\d+)?)°\s*E\s*\|"
    r"\s*(?P<new_name>[^|]+?)\s*\|$"
)

# Hiệu chỉnh theo Nghị quyết 1661/NQ-UBTVQH15 ngày 16/06/2025.
OFFICIAL_CORRECTIONS = {
    "Xã Chiềng Đông": ("Xã Chiềng Đông", "Xã Búng Lao"),
    "Xã Mường Thán": ("Xã Mường Thín", "Xã Chiềng Sinh"),
    "Xã Ẳng Tở": ("Xã Ẳng Tở", "Xã Búng Lao"),
    "Xã Sam Mứn": ("Xã Sam Mứn", "Xã Thanh An"),
    "Xã Keo Lôm": ("Xã Keo Lôm", "Xã Na Son"),
}


def normalize_name(name: str) -> str:
    return re.sub(r"\s+\((?:cũ|mới)\)$", "", name.strip())


def parse_rows(source_path: Path) -> list[tuple[str, str, float, float]]:
    rows = []
    for line in source_path.read_text(encoding="utf-8").splitlines():
        match = ROW_PATTERN.match(line)
        if not match:
            if line.lstrip().startswith("|") and "°" in line:
                raise ValueError(f"Dòng tọa độ sai định dạng: {line}")
            continue
        old_name = normalize_name(match.group("old_name"))
        new_name = normalize_name(match.group("new_name"))
        old_name, new_name = OFFICIAL_CORRECTIONS.get(
            old_name,
            (old_name, new_name),
        )
        rows.append(
            (
                old_name,
                new_name,
                float(match.group("latitude")),
                float(match.group("longitude")),
            )
        )
    return rows
