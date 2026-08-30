"""Yerel API anahtarı ve görünüm tercihi yönetimi."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv, set_key

# Proje kökü (bu dosyanın bir üstü)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = PROJECT_ROOT / ".env"
CONFIG_DIR = Path(
    os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config"))
) / "ceviri-tui"
THEME_PATH = CONFIG_DIR / "theme"


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


def load_theme() -> str | None:
    """Kaydedilmiş Textual tema adını döndürür."""
    try:
        value = THEME_PATH.read_text(encoding="utf-8").strip()
    except OSError:
        return None
    return value or None


def save_theme(theme: str) -> None:
    """Tema tercihini XDG yapılandırma dizininde saklar."""
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        THEME_PATH.write_text(f"{theme}\n", encoding="utf-8")
    except OSError:
        # Tema kalıcılığı uygulamanın çalışmasını engellememeli.
        return
