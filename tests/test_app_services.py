from __future__ import annotations

import unittest
from pathlib import Path

from src.app_services import (
    PreviewRow,
    apply_preview_plan,
    build_preview_rows,
)


class BuildPreviewRowsTests(unittest.TestCase):
    def test_preview_rows_include_reserved_name_warning(self) -> None:
        with TemporaryDir() as temp_dir:
            root = Path(temp_dir)
            (root / "CON.txt").write_text("x", encoding="utf-8")

            rows = build_preview_rows(
                root=root,
                recursive=False,
                include_hidden=False,
                extensions=[],
                separator="_",
                case_mode="preserve",
            )

            self.assertEqual(1, len(rows))
            self.assertEqual("CON.txt", rows[0].source.name)
            self.assertEqual("CON_file.txt", rows[0].target.name)
            self.assertEqual("reserved-name", rows[0].warning)

    def test_preview_rows_include_conflict_warning(self) -> None:
        with TemporaryDir() as temp_dir:
            root = Path(temp_dir)
            (root / "a b.txt").write_text("x", encoding="utf-8")
            (root / "a_b.txt").write_text("y", encoding="utf-8")

            rows = build_preview_rows(
                root=root,
                recursive=False,
                include_hidden=False,
                extensions=[],
                separator="_",
                case_mode="preserve",
            )

            by_source = {row.source.name: row for row in rows}
            self.assertEqual("a_b_1.txt", by_source["a b.txt"].target.name)
            self.assertEqual("name-conflict-risk", by_source["a b.txt"].warning)

    def test_preview_rows_include_dotfile_warning(self) -> None:
        with TemporaryDir() as temp_dir:
            root = Path(temp_dir)
            (root / ".file name").write_text("x", encoding="utf-8")

            rows = build_preview_rows(
                root=root,
                recursive=False,
                include_hidden=True,
                extensions=[],
                separator="_",
                case_mode="preserve",
            )

            self.assertEqual(1, len(rows))
            self.assertEqual(".file_name", rows[0].target.name)
            self.assertEqual("hidden-dotfile", rows[0].warning)


class ApplyPreviewPlanTests(unittest.TestCase):
    def test_apply_preview_plan_reports_success_and_failure(self) -> None:
        with TemporaryDir() as temp_dir:
            root = Path(temp_dir)
            ok_source = root / "good file.txt"
            ok_source.write_text("x", encoding="utf-8")
            bad_source = root / "bad file.txt"
            bad_source.write_text("x", encoding="utf-8")

            rows = [
                PreviewRow(
                    source=ok_source,
                    target=root / "good_file.txt",
                    warning="none",
                ),
                PreviewRow(
                    source=bad_source,
                    target=root / "missing" / "bad_file.txt",
                    warning="none",
                ),
            ]

            summary = apply_preview_plan(rows)

            self.assertEqual(2, summary.attempted)
            self.assertEqual(1, summary.changed)
            self.assertEqual(1, summary.failed)
            self.assertEqual(1, len(summary.failures))
            self.assertEqual("bad file.txt", summary.failures[0].source.name)


class TemporaryDir:
    def __enter__(self) -> str:
        import tempfile

        self._temp = tempfile.TemporaryDirectory()
        return self._temp.__enter__()

    def __exit__(self, exc_type, exc, tb) -> None:
        self._temp.__exit__(exc_type, exc, tb)


if __name__ == "__main__":
    unittest.main()
