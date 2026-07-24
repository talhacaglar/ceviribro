"""Headless açılış duman testi (API anahtarı olmadan)."""

import asyncio
import os
import sys
from pathlib import Path

# Anahtar ortamda olmasın ki ApiKeyScreen tetiklensin
os.environ.pop("DEEPL_AUTH_KEY", None)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ceviri_tui.app import ApiKeyScreen, CeviriApp  # noqa: E402


async def main() -> None:
    app = CeviriApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        # Anahtar yoksa ApiKeyScreen üstte olmalı
        assert isinstance(app.screen, ApiKeyScreen), (
            f"Beklenen ApiKeyScreen, gelen: {type(app.screen).__name__}"
        )
        # Logo ve panel widget'ları ana ekranda mevcut mu?
        base = app.screen_stack[0]
        assert base.query("#logo"), "Logo widget'ı yok"
        assert base.query("#source"), "Kaynak TextArea yok"
        assert base.query("#target"), "Hedef TextArea yok"
        assert base.query("#status-bar"), "Durum çubuğu yok"
        print("SMOKE_OK: ApiKeyScreen açıldı, tüm widget'lar yerinde.")


if __name__ == "__main__":
    asyncio.run(main())
