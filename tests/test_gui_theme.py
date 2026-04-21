"""Утилиты темы GUI (без отображения окна — только расчёт цвета)."""

import tkinter as tk

import pytest

from lang_learn.gui.theme import (
    PALETTE,
    PALETTE_DARK,
    PALETTE_LIGHT,
    apply_professional_theme,
    contrast_select_foreground,
    hex_color_darkened,
    hex_foreground_darkened,
    relative_luminance_hex,
    voice_status_text_font,
)


@pytest.fixture
def tk_root() -> tk.Tk:
    root = tk.Tk()
    root.withdraw()
    try:
        yield root
    finally:
        root.destroy()


def test_hex_color_darkened_gray(tk_root: tk.Tk) -> None:
    out = hex_color_darkened(tk_root, "gray", factor=0.85)
    assert out.startswith("#")
    assert len(out) == 7


def test_hex_foreground_darkened_returns_hex_or_none(tk_root: tk.Tk) -> None:
    out = hex_foreground_darkened(tk_root, factor=0.85)
    assert out is None or (out.startswith("#") and len(out) == 7)


def test_apply_professional_theme_sets_palette(tk_root: tk.Tk) -> None:
    apply_professional_theme(tk_root)
    stored = getattr(tk_root, "_lang_learn_palette", None)
    assert isinstance(stored, dict)
    assert stored["fg"] == PALETTE["fg"] == PALETTE_LIGHT["fg"]
    assert getattr(tk_root, "_lang_learn_fg_dark", None) == PALETTE["fg"]
    assert getattr(tk_root, "_lang_learn_theme_variant", None) == "light"


def test_apply_professional_theme_light_variant(tk_root: tk.Tk) -> None:
    apply_professional_theme(tk_root, variant="light")
    stored = getattr(tk_root, "_lang_learn_palette", None)
    assert isinstance(stored, dict)
    assert stored["fg"] == PALETTE_LIGHT["fg"]
    assert getattr(tk_root, "_lang_learn_theme_variant", None) == "light"


def test_apply_professional_theme_dark_variant(tk_root: tk.Tk) -> None:
    apply_professional_theme(tk_root, variant="dark")
    stored = getattr(tk_root, "_lang_learn_palette", None)
    assert isinstance(stored, dict)
    assert stored["fg"] == PALETTE_DARK["fg"]
    assert getattr(tk_root, "_lang_learn_theme_variant", None) == "dark"


def test_contrast_select_foreground_light_vs_dark_band() -> None:
    """На светлой полосе выделения — тёмные буквы, на тёмной — светлые."""
    assert contrast_select_foreground("#ffffff") == "#0f172a"
    assert contrast_select_foreground("#c7d2e0") == "#0f172a"
    assert contrast_select_foreground("#1e4a8c") == "#f8fafc"
    assert contrast_select_foreground("#3d5280") == "#f8fafc"


def test_relative_luminance_hex_bounds() -> None:
    assert 0.0 <= relative_luminance_hex("#000000") <= 0.05
    assert relative_luminance_hex("#ffffff") >= 0.95


def test_palette_stored_select_colors_contrast(tk_root: tk.Tk) -> None:
    """Сохранённая палитра: фон выделения и цвет текста по разные стороны порога."""
    apply_professional_theme(tk_root, variant="light")
    pal = getattr(tk_root, "_lang_learn_palette")
    lum_bg = relative_luminance_hex(pal["selectbackground"])
    lum_fg = relative_luminance_hex(pal["selectforeground"])
    assert (lum_bg > 0.42) != (lum_fg > 0.42)

    apply_professional_theme(tk_root, variant="dark")
    pal_d = getattr(tk_root, "_lang_learn_palette")
    lum_bg_d = relative_luminance_hex(pal_d["selectbackground"])
    lum_fg_d = relative_luminance_hex(pal_d["selectforeground"])
    assert (lum_bg_d > 0.42) != (lum_fg_d > 0.42)


def test_voice_status_text_font_matches_shape(tk_root: tk.Tk) -> None:
    apply_professional_theme(tk_root, variant="light")
    fam, size, weight = voice_status_text_font()
    assert isinstance(fam, str) and fam
    assert isinstance(size, int) and size >= 6
    assert weight == "bold"
