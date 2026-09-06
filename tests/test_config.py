"""Dil tercihlerinin güvenli okunması ve saklanması."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from ceviri_tui import config


class LanguageConfigTests(unittest.TestCase):
    def test_roundtrip_and_invalid_files(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(config, "CONFIG_DIR", Path(directory)):
                self.assertEqual(config.load_languages(), (None, "TR"))
                self.assertTrue(config.save_languages("DE", "PT-BR"))
                self.assertEqual(config.load_languages(), ("DE", "PT-BR"))
                for value in ["{", "[]", "null", '{}', '{"source": 1, "target": "TR"}']:
                    (Path(directory) / "languages.json").write_text(value)
                    self.assertEqual(config.load_languages(), (None, "TR"))

    def test_unwritable_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / "file"
            file.touch()
            with patch.object(config, "CONFIG_DIR", file):
                self.assertFalse(config.save_languages(None, "TR"))
