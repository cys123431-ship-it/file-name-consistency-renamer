from __future__ import annotations

import re
from pathlib import Path

from src.app_services import ApplySummary


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


def format_apply_summary(summary: ApplySummary) -> str:
    lines = [
        f"Attempted: {summary.attempted}",
        f"Changed: {summary.changed}",
        f"Failed: {summary.failed}",
    ]
    if summary.failures:
        lines.append(f"First error: {summary.failures[0].error}")
    return "\n".join(lines)
