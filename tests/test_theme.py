"""Sistem teması eşlemesinin ağsız testleri."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from ceviri_tui.theme import FALLBACK_PALETTE, build_themes, load_system_palette


class ThemeTests(unittest.TestCase):
    def test_active_omarchy_colors_are_loaded(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            colors_path = Path(directory) / "colors.toml"
            colors_path.write_text(
                '\n'.join(
                    [
                        'accent = "#123456"',
                        'foreground = "#fefefe"',
                        'background = "#010203"',
                        'color1 = "#aabbcc"',
                        '[ignored]',
                        'color2 = "#000000"',
                    ]
                ),
                encoding="utf-8",
            )

            palette = load_system_palette(colors_path)

        self.assertEqual(palette["accent"], "#123456")
        self.assertEqual(palette["foreground"], "#fefefe")
        self.assertEqual(palette["background"], "#010203")
        self.assertEqual(palette["color1"], "#aabbcc")
        self.assertEqual(palette["color2"], FALLBACK_PALETTE["color2"])

    def test_missing_system_theme_uses_fallback(self) -> None:
        palette = load_system_palette(Path("/missing/omarchy/colors.toml"))

        self.assertEqual(palette, FALLBACK_PALETTE)

    def test_theme_names_remain_compatible_with_saved_preferences(self) -> None:
        dark, light = build_themes(FALLBACK_PALETTE)

        self.assertEqual(dark.name, "dtr-dark")
        self.assertEqual(light.name, "dtr-light")


if __name__ == "__main__":
    unittest.main()
