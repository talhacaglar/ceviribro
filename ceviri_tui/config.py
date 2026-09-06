"""Yerel API anahtarı ve görünüm tercihi yönetimi."""

from __future__ import annotations

import json
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


def load_languages() -> tuple[str | None, str]:
    """Son dil çiftini okur; bozuk dosyada başlangıç değerlerini kullanır."""
    try:
        data = json.loads((CONFIG_DIR / "languages.json").read_text(encoding="utf-8"))
        source, target = data["source"], data["target"]
        def valid(code):
            return isinstance(code, str) and 2 <= len(code) <= 12 and all(
                part.isalpha() and part.isupper() for part in code.split("-")
            )
        if (source is None or valid(source)) and valid(target):
            return source, target
    except (OSError, ValueError, KeyError, TypeError):
        pass
    return None, "TR"


def save_languages(source: str | None, target: str) -> bool:
    """Dil çiftini tek dosyada atomik olarak saklar."""
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        temporary = CONFIG_DIR / "languages.json.tmp"
        temporary.write_text(
            json.dumps({"source": source, "target": target}) + "\n", encoding="utf-8"
        )
        temporary.replace(CONFIG_DIR / "languages.json")
    except OSError:
        return False
    return True
