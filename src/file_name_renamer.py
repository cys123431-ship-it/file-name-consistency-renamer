#!/usr/bin/env python3
"""
Windows-friendly filename consistency renamer.
"""

from __future__ import annotations

import argparse
import os
import re
import unicodedata
from pathlib import Path

INVALID_WIN_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1F]')
NON_NAME_CHARS = re.compile(r"[^\w\-\.\uAC00-\uD7A3]+", re.UNICODE)
RESERVED_BASENAMES = {
    "con", "prn", "aux", "nul",
    "com1", "com2", "com3", "com4", "com5", "com6", "com7", "com8", "com9",
    "lpt1", "lpt2", "lpt3", "lpt4", "lpt5", "lpt6", "lpt7", "lpt8", "lpt9",
}


def normalize_stem(stem: str, separator: str, case_mode: str) -> str:
    stem = unicodedata.normalize("NFKC", stem).strip()
    stem = stem.replace("\u200b", "")
    stem = INVALID_WIN_CHARS.sub(" ", stem)
    stem = NON_NAME_CHARS.sub(separator, stem)
    stem = re.sub(fr"{re.escape(separator)}+", separator, stem).strip(f". {separator}")

    if case_mode == "lower":
        stem = stem.lower()
    elif case_mode == "upper":
        stem = stem.upper()

    if not stem:
        stem = "renamed_file"

    if stem.casefold() in RESERVED_BASENAMES:
        stem = f"{stem}_file"

    return stem


def make_new_path(path: Path, separator: str, case_mode: str) -> Path:
    original_name = path.name
    if original_name.startswith(".") and original_name.count(".") == 1:
        stem = original_name[1:]
        ext = ""
        was_hidden_dot = True
    else:
        stem = path.stem
        ext = path.suffix
        was_hidden_dot = False

    stem = normalize_stem(stem, separator=separator, case_mode=case_mode)
    if was_hidden_dot:
        stem = f".{stem}"
    return path.with_name(f"{stem}{ext}")


def gather_files(root: Path, recursive: bool, include_hidden: bool, extensions: list[str]) -> list[Path]:
    if recursive:
        candidates = root.rglob("*")
    else:
        candidates = root.iterdir()

    allowed_exts = {e.lower() if e.startswith(".") else f".{e.lower()}" for e in extensions}

    files = []
    for path in candidates:
        if not path.is_file():
            continue
        if not include_hidden and path.name.startswith("."):
            continue
        if extensions and path.suffix.lower() not in allowed_exts:
            continue
        files.append(path)

    files.sort(key=lambda p: (str(p.parent).lower(), p.name.lower()))
    return files


def plan_renames(paths: list[Path], separator: str, case_mode: str) -> list[tuple[Path, Path]]:
    names_in_dir: dict[Path, set[str]] = {
        path.parent: {p.name.casefold() for p in path.parent.iterdir()}
        for path in paths
    }

    plan = []
    for src in paths:
        parent = src.parent
        occupied = names_in_dir[parent]

        dst = make_new_path(src, separator=separator, case_mode=case_mode)
        proposed = dst.name
        base = src.name.casefold()

        if proposed.casefold() == src.name.casefold():
            continue

        if base in occupied:
            occupied.remove(base)

        stem = dst.stem
        ext = src.suffix

        candidate = proposed
        idx = 1
        while candidate.casefold() in occupied:
            candidate = f"{stem}_{idx}{ext}"
            idx += 1

        dst = src.with_name(candidate)
        plan.append((src, dst))
        occupied.add(candidate.casefold())

    return plan


def execute(plan: list[tuple[Path, Path]], dry_run: bool) -> None:
    if not plan:
        print("변경할 파일이 없습니다.")
        return

    for src, dst in plan:
        print(f"{src.name} -> {dst.name}")
        if not dry_run:
            src.rename(dst)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="윈도우즈용 파일명 일관 정리 프로그램"
    )
    parser.add_argument("path", nargs="?", default=".", help="대상 폴더 (기본: 현재 폴더)")
    parser.add_argument(
        "-r", "--recursive", action="store_true",
        help="하위 폴더까지 파일명을 재귀적으로 변경"
    )
    parser.add_argument(
        "--separator",
        default="_",
        choices=["_", "-", "."],
        help="허용되지 않는 문자 대체 구분자 (기본: _)"
    )
    parser.add_argument(
        "--case",
        default="lower",
        choices=["lower", "upper", "preserve"],
        help="대문자/소문자 처리 방식 (기본: lower)"
    )
    parser.add_argument(
        "--include-hidden",
        action="store_true",
        help="점(.)으로 시작하는 숨김 파일도 처리"
    )
    parser.add_argument(
        "--extensions",
        nargs="*",
        default=[],
        help="특정 확장자만 처리 (.txt .jpg ...). 미지정 시 전체 처리"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="실제 변경 없이 미리보기만 표시"
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.path).resolve()

    if not root.exists() or not root.is_dir():
        raise SystemExit("지정한 경로가 폴더가 아닙니다.")

    paths = gather_files(root, args.recursive, args.include_hidden, args.extensions)
    plan = plan_renames(paths, separator=args.separator, case_mode=args.case)
    execute(plan, args.dry_run)

    if args.dry_run:
        print(f"예상 변경 건수: {len(plan)}개")
    else:
        print(f"변경 완료: {len(plan)}개")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
