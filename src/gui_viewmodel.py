from __future__ import annotations

import re
from pathlib import Path


def parse_extensions_input(raw: str) -> list[str]:
    tokens = re.split(r"[,\s;]+", raw.strip())
    seen: set[str] = set()
    normalized: list[str] = []

    for token in tokens:
        if not token:
            continue
        value = token.lower()
        if not value.startswith("."):
            value = f".{value}"
        if value in seen:
            continue
        seen.add(value)
        normalized.append(value)

    return normalized


def validate_folder_path(raw: str) -> tuple[bool, str]:
    cleaned = raw.strip()
    if not cleaned:
        return False, "Folder path is required."

    path = Path(cleaned).expanduser()
    if not path.exists():
        return False, f"Folder does not exist: {cleaned}"
    if not path.is_dir():
        return False, f"Path is not a directory: {cleaned}"
    return True, str(path.resolve())
