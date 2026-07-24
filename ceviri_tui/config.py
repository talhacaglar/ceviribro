"""API anahtarı ve yapılandırma yönetimi."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv, set_key

# Proje kökü (bu dosyanın bir üstü)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = PROJECT_ROOT / ".env"


def load_api_key() -> str | None:
    """.env dosyasından veya ortam değişkeninden DeepL API anahtarını okur."""
    if ENV_PATH.exists():
        load_dotenv(ENV_PATH, override=False)
    key = os.getenv("DEEPL_AUTH_KEY")
    if key:
        key = key.strip().strip('"').strip("'")
    return key or None


def save_api_key(key: str) -> None:
    """API anahtarını .env dosyasına yazar (yoksa oluşturur)."""
    key = key.strip()
    if not ENV_PATH.exists():
        ENV_PATH.write_text("", encoding="utf-8")
    # set_key değeri tırnaklamadan yazsın diye quote_mode="never"
    set_key(str(ENV_PATH), "DEEPL_AUTH_KEY", key, quote_mode="never")
    os.environ["DEEPL_AUTH_KEY"] = key
