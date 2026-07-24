"""Çeviri akışı testi — DeepL'e gitmeden sahte çevirmenle."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from textual.widgets import ListView, TextArea  # noqa: E402

from ceviri_tui.app import CeviriApp  # noqa: E402
from ceviri_tui.translator import UsageInfo  # noqa: E402


class FakeTranslator:
    def translate(self, text, target_lang="TR"):
        return ("Merhaba dünya", "EN")

    def get_usage(self):
        return UsageInfo(count=1234, limit=500000)


async def main() -> None:
    app = CeviriApp()
    async with app.run_test() as pilot:
        # Anahtar ekranını atlayıp sahte çevirmeni enjekte et
        if app.screen_stack[-1] is not app.screen_stack[0]:
            app.pop_screen()
        app.translator = FakeTranslator()
        await pilot.pause()

        src = app.query_one("#source", TextArea)
        src.text = "Hello world"
        app.action_translate()
        # thread worker'ın çeviriyi uygulamasını bekle (kısa polling)
        tgt = app.query_one("#target", TextArea)
        for _ in range(50):
            await pilot.pause()
            if tgt.text:
                break
        assert tgt.text == "Merhaba dünya", f"Çeviri hatalı: {tgt.text!r}"

        history = app.query_one("#history", ListView)
        assert len(history.children) == 1, "Geçmişe eklenmedi"

        # Temizleme çalışıyor mu?
        app.action_clear()
        await pilot.pause()
        assert app.query_one("#source", TextArea).text == ""
        assert app.query_one("#target", TextArea).text == ""
        print("FLOW_OK: çeviri, geçmiş, kopyala, temizle çalışıyor.")


if __name__ == "__main__":
    asyncio.run(main())
