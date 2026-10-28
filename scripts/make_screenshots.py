"""README ve görsel QA için ağsız ceviribro ekran görüntüleri üretir."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from textual.widgets import TextArea

from ceviribro.app import CeviriApp, LIGHT_THEME
from ceviribro.translator import UsageInfo

ASSETS = ROOT / "assets"


class PreviewTranslator:
    def translate(
        self,
        text: str,
        target_lang: str = "TR",
        source_lang: str | None = None,
    ) -> tuple[str, str]:
        if target_lang == "EN":
            return "The city feels quieter after midnight.", "TR"
        return "Şehir gece yarısından sonra daha sessiz geliyor.", "EN"

    def get_usage(self) -> UsageInfo:
        return UsageInfo(count=12_480, limit=500_000)


async def capture(name: str, size: tuple[int, int], light: bool = False) -> None:
    app = CeviriApp(translator=PreviewTranslator())
    async with app.run_test(size=size) as pilot:
        if light:
            app.theme = LIGHT_THEME.name
        source = app.query_one("#source", TextArea)
        source.text = "The city feels quieter after midnight."
        app.action_translate()
        for _ in range(30):
            await pilot.pause()
            if app.query_one("#target", TextArea).text:
                break
        await pilot.pause()
        await pilot.pause()
        app.save_screenshot(filename=f"{name}.svg", path=str(ASSETS))


async def main() -> None:
    ASSETS.mkdir(exist_ok=True)
    await capture("screenshot-dark", (96, 30))
    await capture("screenshot-light", (96, 30), light=True)
    await capture("screenshot-compact", (72, 24))


if __name__ == "__main__":
    asyncio.run(main())
