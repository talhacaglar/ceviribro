"""DTR arayüzünün ağsız davranış testleri."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from textual.widgets import Button, Static, TextArea, Select

from ceviri_tui import config
from ceviri_tui.app import ApiKeyScreen, CeviriApp, LIGHT_THEME
from ceviri_tui.translator import UsageInfo


class FakeTranslator:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str, str | None]] = []

    def translate(
        self,
        text: str,
        target_lang: str = "TR",
        source_lang: str | None = None,
    ) -> tuple[str, str]:
        self.calls.append((text, target_lang, source_lang))
        if target_lang == "EN":
            return "Hello world", "TR"
        return "Merhaba dünya", "EN"

    def get_languages(self):
        return (
            {"TR": "Türkçe", "EN": "English", "DE": "German", "JA": "Japanese"},
            {"TR": "Türkçe", "EN-US": "English (American)", "DE": "German", "JA": "Japanese"},
        )

    def get_usage(self) -> UsageInfo:
        return UsageInfo(count=1_234, limit=500_000)


async def wait_for_text(pilot, widget: TextArea, expected: str) -> None:
    for _ in range(80):
        await pilot.pause()
        if widget.text == expected:
            return
    raise AssertionError(f"Beklenen çeviri gelmedi: {widget.text!r}")


class AppTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        patcher = patch.object(config, "CONFIG_DIR", Path(directory.name))
        patcher.start()
        self.addCleanup(patcher.stop)

    async def test_language_selection_survives_restart(self):
        translator = FakeTranslator()
        app = CeviriApp(translator=translator)
        async with app.run_test(size=(72, 24)) as pilot:
            await pilot.pause()
            app.query_one("#source-select", Select).value = "DE"
            app.query_one("#target-select", Select).value = "JA"
            await pilot.pause()
            self.assertEqual(config.load_languages(), ("DE", "JA"))
            app.query_one("#source", TextArea).text = "Hallo"
            app.action_translate()
            await wait_for_text(pilot, app.query_one("#target", TextArea), "Merhaba dünya")
            self.assertEqual(translator.calls[-1], ("Hallo", "JA", "DE"))
            old_generation = app._translation_generation
            app.action_clear()
            app.query_one("#target-select", Select).value = "TR"
            await pilot.pause()
            app._apply_translation("Hallo", "stale", "DE", "JA", old_generation)
            self.assertEqual(app.query_one("#target", TextArea).text, "")
            app.query_one("#target-select", Select).value = "JA"
            await pilot.pause()

        restored = CeviriApp(translator=FakeTranslator())
        async with restored.run_test(size=(72, 24)) as pilot:
            await pilot.pause()
            self.assertEqual(restored.query_one("#source-select", Select).value, "DE")
            self.assertEqual(restored.query_one("#target-select", Select).value, "JA")
            restored.query_one("#source-select", Select).value = "AUTO"
            await pilot.pause()
            self.assertEqual(config.load_languages(), (None, "JA"))

    async def test_app_flows(self) -> None:
        await self._check_translation_modes_counts_and_clear()
        await self._check_ctrl_e_has_priority_inside_editor()
        await self._check_theme_is_persisted()
        await self._check_missing_api_key_opens_setup_screen()

    async def _check_translation_modes_counts_and_clear(self) -> None:
        translator = FakeTranslator()
        app = CeviriApp(translator=translator)

        async with app.run_test(size=(96, 30)) as pilot:
            source = app.query_one("#source", TextArea)
            target = app.query_one("#target", TextArea)
            source.text = "Hello world"
            app.action_translate()
            await wait_for_text(pilot, target, "Merhaba dünya")

            self.assertEqual(translator.calls[-1], ("Hello world", "TR", None))
            self.assertEqual(str(app.query_one("#source-count", Static).content), "11 KARAKTER")
            self.assertEqual(str(app.query_one("#target-count", Static).content), "13 KARAKTER")

            await pilot.press("f4")
            await wait_for_text(pilot, target, "Hello world")
            self.assertEqual(translator.calls[-1], ("Hello world", "EN", "TR"))
            self.assertTrue(app.query_one("#mode-en", Button).has_class("active"))

            app.action_clear()
            await pilot.pause()
            self.assertEqual(source.text, "")
            self.assertEqual(target.text, "")

    async def _check_ctrl_e_has_priority_inside_editor(self) -> None:
        translator = FakeTranslator()
        app = CeviriApp(translator=translator)

        async with app.run_test(size=(72, 24)) as pilot:
            app.query_one("#source", TextArea).focus()
            await pilot.press("ctrl+e")
            self.assertEqual(app._target_lang, "EN")
            self.assertEqual(app._source_lang_override, "TR")

    async def _check_theme_is_persisted(self) -> None:
        translator = FakeTranslator()
        with tempfile.TemporaryDirectory() as directory:
            config_dir = Path(directory)
            with (
                patch.object(config, "CONFIG_DIR", config_dir),
                patch.object(config, "THEME_PATH", config_dir / "theme"),
            ):
                app = CeviriApp(translator=translator)
                async with app.run_test() as pilot:
                    app.action_toggle_theme()
                    await pilot.pause()
                    self.assertEqual(app.theme, LIGHT_THEME.name)
                    self.assertEqual(config.load_theme(), LIGHT_THEME.name)

    async def _check_missing_api_key_opens_setup_screen(self) -> None:
        with patch("ceviri_tui.app.load_api_key", return_value=None):
            app = CeviriApp()
            async with app.run_test() as pilot:
                await pilot.pause()
                self.assertIsInstance(app.screen, ApiKeyScreen)
                base = app.screen_stack[0]
                self.assertTrue(base.query("#source"))
                self.assertTrue(base.query("#target"))
                self.assertTrue(base.query("#direction-rail"))


if __name__ == "__main__":
    unittest.main()
