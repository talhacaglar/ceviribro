"""ceviribro temasını etkin Omarchy paletiyle hizalar."""

from __future__ import annotations

import re
from pathlib import Path

from textual.theme import Theme

OMARCHY_COLORS_PATH = (
    Path.home() / ".local" / "state" / "omarchy" / "current" / "theme" / "colors.toml"
)

FALLBACK_PALETTE = {
    "foreground": "#FAFCFB",
    "background": "#0c0b0c",
    "accent": "#b59790",
    "color1": "#c38b7b",
    "color2": "#87a9b0",
    "color6": "#a5a0b6",
    "color8": "#584e51",
    "color15": "#e2dddc",
}

_COLOR_ASSIGNMENT = re.compile(
    r'^([A-Za-z0-9_-]+)\s*=\s*"(#[0-9A-Fa-f]{6})"\s*(?:#.*)?$'
)


def load_system_palette(path: Path = OMARCHY_COLORS_PATH) -> dict[str, str]:
    """Etkin Omarchy renklerini okur; mevcut değilse yerleşik paleti kullanır."""
    palette = FALLBACK_PALETTE.copy()
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return palette

    for raw_line in lines:
        line = raw_line.strip()
        if line.startswith("["):
            break
        match = _COLOR_ASSIGNMENT.fullmatch(line)
        if match and match.group(1) in palette:
            palette[match.group(1)] = match.group(2)
    return palette


def build_themes(palette: dict[str, str] | None = None) -> tuple[Theme, Theme]:
    """Sistem paletinden uyumlu koyu ve açık Textual temaları üretir."""
    colors = palette or load_system_palette()
    dark = Theme(
        name="ceviribro-dark",
        primary=colors["color8"],
        secondary=colors["color6"],
        accent=colors["accent"],
        success=colors["color2"],
        warning=colors["color6"],
        error=colors["color1"],
        foreground=colors["foreground"],
        background=colors["background"],
        surface="#141314",
        panel="#1c1a1b",
        dark=True,
    )
    light = Theme(
        name="ceviribro-light",
        primary=colors["color6"],
        secondary=colors["color8"],
        accent="#6B5E73",
        success="#55777e",
        warning="#765e69",
        error="#9d5e50",
        foreground=colors["background"],
        background=colors["foreground"],
        surface="#f2f0f0",
        panel=colors["color15"],
        dark=False,
    )
    return dark, light
