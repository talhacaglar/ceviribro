"""DeepL çeviri sarmalayıcısı."""

from __future__ import annotations

from dataclasses import dataclass

import deepl

TARGET_LANG_ALIASES = {"EN": "EN-US"}


@dataclass
class UsageInfo:
    """DeepL kota bilgisi."""

    count: int
    limit: int

    @property
    def ratio(self) -> float:
        if self.limit <= 0:
            return 0.0
        return self.count / self.limit


class TranslationError(Exception):
    """Çeviri sırasında oluşan hataları sarmalar."""


class Translator:
    """DeepL API'sini saran basit çeviri istemcisi."""

    def __init__(self, auth_key: str) -> None:
        if not auth_key:
            raise TranslationError("DeepL API anahtarı boş olamaz.")
        try:
            self._client = deepl.Translator(auth_key)
        except Exception as exc:  # pragma: no cover - kütüphane hataları
            raise TranslationError(f"DeepL istemcisi oluşturulamadı: {exc}") from exc

    def translate(
        self,
        text: str,
        target_lang: str = "TR",
        source_lang: str | None = None,
    ) -> tuple[str, str]:
        """Metni hedef dile çevirir.

        Returns:
            (çeviri_metni, algılanan_kaynak_dil)
        """
        text = text.strip()
        if not text:
            return "", ""
        try:
            api_target_lang = TARGET_LANG_ALIASES.get(target_lang, target_lang)
            options: dict[str, str] = {"target_lang": api_target_lang}
            if source_lang is not None:
                options["source_lang"] = source_lang
            result = self._client.translate_text(text, **options)
        except deepl.DeepLException as exc:
            raise TranslationError(f"DeepL hatası: {exc}") from exc
        except Exception as exc:  # pragma: no cover
            raise TranslationError(f"Beklenmeyen hata: {exc}") from exc
        return result.text, result.detected_source_lang

    def get_languages(self) -> tuple[dict[str, str], dict[str, str]]:
        """DeepL tarafından desteklenen kaynak ve hedef dilleri getirir."""
        try:
            sources = {lang.code: lang.name for lang in self._client.get_source_languages()}
            targets = {lang.code: lang.name for lang in self._client.get_target_languages()}
            if not sources or not targets:
                raise TranslationError("DeepL dil listesi boş döndü.")
            return sources, targets
        except deepl.DeepLException as exc:
            raise TranslationError(f"Diller alınamadı: {exc}") from exc

    def get_usage(self) -> UsageInfo | None:
        """Karakter kotası bilgisini döndürür (alınamazsa None)."""
        try:
            usage = self._client.get_usage()
        except Exception:
            return None
        if usage.character is None:
            return None
        return UsageInfo(
            count=usage.character.count,
            limit=usage.character.limit,
        )
