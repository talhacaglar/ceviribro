"""DeepL sarmalayıcısının yön ve hata sözleşmesi."""

from __future__ import annotations

import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from ceviri_tui.translator import Translator


class TranslatorTests(unittest.TestCase):
    @patch("ceviri_tui.translator.deepl.Translator")
    def test_source_language_is_only_sent_when_explicit(self, client_type: Mock) -> None:
        client = client_type.return_value
        client.translate_text.return_value = SimpleNamespace(
            text="Hello", detected_source_lang="TR"
        )
        translator = Translator("test-key")

        translator.translate("Merhaba", target_lang="EN", source_lang="TR")

        client.translate_text.assert_called_once_with(
            "Merhaba", target_lang="EN-US", source_lang="TR"
        )

    @patch("ceviri_tui.translator.deepl.Translator")
    def test_automatic_detection_omits_source_language(self, client_type: Mock) -> None:
        client = client_type.return_value
        client.translate_text.return_value = SimpleNamespace(
            text="Merhaba", detected_source_lang="EN"
        )
        translator = Translator("test-key")

        translator.translate("Hello", target_lang="TR")

        client.translate_text.assert_called_once_with("Hello", target_lang="TR")


if __name__ == "__main__":
    unittest.main()
