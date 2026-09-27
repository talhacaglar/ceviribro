"""Dil tercihlerinin güvenli okunması ve saklanması."""
import tempfile
import os
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


class ApiKeyConfigTests(unittest.TestCase):
    def test_save_uses_writable_user_directory_and_private_permissions(self):
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, {}, clear=True):
            root = Path(directory)
            user_env = root / "user-config/.env"
            legacy_env = root / "package/.env"
            with patch.object(config, "ENV_PATH", user_env), patch.object(config, "LEGACY_ENV_PATH", legacy_env):
                config.save_api_key("dummy-key")
                self.assertEqual(user_env.stat().st_mode & 0o777, 0o600)
                self.assertFalse(legacy_env.exists())
                os.environ.pop("DEEPL_AUTH_KEY")
                self.assertEqual(config.load_api_key(), "dummy-key")

    def test_environment_then_user_then_legacy_precedence(self):
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, {}, clear=True):
            root = Path(directory)
            user_env, legacy_env = root / "user.env", root / "legacy.env"
            user_env.write_text("DEEPL_AUTH_KEY=user-key\n")
            legacy_env.write_text("DEEPL_AUTH_KEY=legacy-key\n")
            with patch.object(config, "ENV_PATH", user_env), patch.object(config, "LEGACY_ENV_PATH", legacy_env):
                os.environ["DEEPL_AUTH_KEY"] = "environment-key"
                self.assertEqual(config.load_api_key(), "environment-key")
                os.environ.pop("DEEPL_AUTH_KEY")
                self.assertEqual(config.load_api_key(), "user-key")
                os.environ.pop("DEEPL_AUTH_KEY")
                user_env.unlink()
                self.assertEqual(config.load_api_key(), "legacy-key")
