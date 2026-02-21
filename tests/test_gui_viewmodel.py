from __future__ import annotations

import unittest
from pathlib import Path

from src.gui_viewmodel import parse_extensions_input, validate_folder_path


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


if __name__ == "__main__":
    unittest.main()
