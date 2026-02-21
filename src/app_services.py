from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from src.file_name_renamer import (
    RESERVED_BASENAMES,
    gather_files,
    make_new_path,
    plan_renames,
)


@dataclass(frozen=True)
class PreviewRow:
    source: Path
    target: Path
    warning: str


@dataclass(frozen=True)
class ApplyFailure:
    source: Path
    target: Path
    error: str


@dataclass(frozen=True)
class ApplySummary:
    attempted: int
    changed: int
    failed: int
    failures: list[ApplyFailure]


def _is_hidden_dotfile(path: Path) -> bool:
    return path.name.startswith(".") and path.name.count(".") == 1


def _source_stem_for_warning(path: Path) -> str:
    if _is_hidden_dotfile(path):
        return path.name[1:]
    return path.stem


def _warning_for_row(
    source: Path,
    target: Path,
    separator: str,
    case_mode: str,
) -> str:
    source_stem = _source_stem_for_warning(source).casefold()
    if source_stem in RESERVED_BASENAMES:
        return "reserved-name"

    proposed_name = make_new_path(
        source,
        separator=separator,
        case_mode=case_mode,
    ).name
    if proposed_name.casefold() != target.name.casefold():
        return "name-conflict-risk"

    if _is_hidden_dotfile(source):
        return "hidden-dotfile"

    return "none"


def build_preview_rows(
    root: Path | str,
    recursive: bool,
    include_hidden: bool,
    extensions: list[str],
    separator: str,
    case_mode: str,
) -> list[PreviewRow]:
    root_path = Path(root)
    files = gather_files(
        root=root_path,
        recursive=recursive,
        include_hidden=include_hidden,
        extensions=extensions,
    )
    plan = plan_renames(
        files,
        separator=separator,
        case_mode=case_mode,
    )

    rows: list[PreviewRow] = []
    for source, target in plan:
        rows.append(
            PreviewRow(
                source=source,
                target=target,
                warning=_warning_for_row(
                    source=source,
                    target=target,
                    separator=separator,
                    case_mode=case_mode,
                ),
            )
        )

    return rows


def apply_preview_plan(rows: Sequence[PreviewRow]) -> ApplySummary:
    failures: list[ApplyFailure] = []
    changed = 0

    for row in rows:
        try:
            row.source.rename(row.target)
            changed += 1
        except OSError as exc:
            failures.append(
                ApplyFailure(
                    source=row.source,
                    target=row.target,
                    error=str(exc),
                )
            )

    return ApplySummary(
        attempted=len(rows),
        changed=changed,
        failed=len(failures),
        failures=failures,
    )
