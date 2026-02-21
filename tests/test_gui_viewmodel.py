from __future__ import annotations

import unittest
from pathlib import Path

from src.app_services import ApplyFailure, ApplySummary
from src.gui_viewmodel import (
    format_apply_summary,
    parse_extensions_input,
    validate_folder_path,
)


class ParseExtensionsInputTests(unittest.TestCase):
    def test_parse_extensions_input_normalizes_values(self) -> None:
        parsed = parse_extensions_input(".png jpg, .jpeg ,txt, jpg")
        self.assertEqual([".png", ".jpg", ".jpeg", ".txt"], parsed)

    def test_parse_extensions_input_ignores_empty_tokens(self) -> None:
        parsed = parse_extensions_input(" , ,, ")
        self.assertEqual([], parsed)


class ValidateFolderPathTests(unittest.TestCase):
    def test_validate_folder_path_rejects_missing_directory(self) -> None:
        ok, message = validate_folder_path("D:/missing/path")
        self.assertFalse(ok)
        self.assertIn("does not exist", message)

    def test_validate_folder_path_accepts_existing_directory(self) -> None:
        ok, message = validate_folder_path(str(Path.cwd()))
        self.assertTrue(ok)
        self.assertTrue(message)


class FormatApplySummaryTests(unittest.TestCase):
    def test_format_apply_summary_contains_counts_and_first_error(self) -> None:
        summary = ApplySummary(
            attempted=10,
            changed=9,
            failed=1,
            failures=[
                ApplyFailure(
                    source=Path("a.txt"),
                    target=Path("b.txt"),
                    error="permission denied",
                )
            ],
        )
        text = format_apply_summary(summary)
        self.assertIn("Attempted: 10", text)
        self.assertIn("Changed: 9", text)
        self.assertIn("Failed: 1", text)
        self.assertIn("permission denied", text)


if __name__ == "__main__":
    unittest.main()
