"""
Палитра цветов и оформление виджетов ttk (тема «clam») для учебного окна.

Файл задаёт:
  - словари ``PALETTE_LIGHT`` / ``PALETTE_DARK`` — именованные цвета интерфейса;
  - ``apply_professional_theme`` — применение палитры и стилей к ``Tk`` после
    настройки шрифтов (вызывается из ``desktop_chat.apply_global_ui_fonts``);
  - ``style_text_widget`` — оформление классических ``Text``/``ScrolledText``;
  - ``voice_status_text_font`` — жирный кегль +2 pt (как у статуса урока).

Как подстраивать:
  - Меняйте hex-значения в ``PALETTE_*``: ключи вида ``bg_*`` — фоны,
    ``bg_section_params`` / ``bg_section_content`` / ``bg_section_progress`` —
    три оттенка главных зон окна (параметры, вкладки урок/диалог, прогресс);
    ``fg*`` — текст, ``accent*`` — кнопки-акценты и курсор, ``select*`` —
    выделение в полях, ``bg_button_*`` — фон кнопок при наведении/нажатии.
  - В ``apply_professional_theme`` правьте ``padding`` у вкладок/кнопок
    (гориз., верт., в пикселях для ttk) и ``font=`` у стилей — кегль и начертание.
  - ``variant`` при вызове темы: ``light`` или ``dark`` — какой словарь палитры
    подставляется целиком.

Тесты в ``tests/test_gui_theme.py`` опираются на наличие ключей в палитрах.
"""

from __future__ import annotations

import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk
from typing import Literal, Mapping

# Светлая палитра: белый фон окна, чёрный текст; центральная зона — голубее боковых.
# Все ключи используются в apply_professional_theme и/или style_text_widget.
PALETTE_LIGHT: dict[str, str] = {
    "bg_app": "#ffffff",
    # Боковые зоны — сине-серые; центр (урок/диалог) — сильнее голубой.
    "bg_section_params": "#e9ecf1",
    "bg_section_content": "#cce8f4",
    "bg_section_progress": "#e2e7ef",
    "bg_card": "#cce8f4",
    "bg_panel": "#d8e9f4",
    "bg_elevated": "#d4e7f2",
    "bg_tab": "#b8daf0",
    "fg": "#000000",
    "fg_secondary": "#000000",
    "fg_muted": "#404040",
    "border": "#ffffff",
    "accent": "#000000",
    "accent_hover": "#222222",
    "accent_pressed": "#000000",
    "on_accent": "#ffffff",
    "entry_bg": "#ffffff",
    "text_area_bg": "#f0f7fb",
    "selectbackground": "#c8c8c8",
    "selectforeground": "#000000",
    "bg_button_active": "#eeeeee",
    "bg_button_pressed": "#e5e5e5",
}

# Тёмная палитра: те же ключи, что у светлой; другие значения hex.
PALETTE_DARK: dict[str, str] = {
    "bg_app": "#121418",
    "bg_section_params": "#1a1f28",
    "bg_section_content": "#152a3d",
    "bg_section_progress": "#222a38",
    "bg_card": "#152a3d",
    "bg_panel": "#252a34",
    "bg_elevated": "#1e222a",
    "bg_tab": "#2f3542",
    "fg": "#e6eaf0",
    "fg_secondary": "#a8b0bd",
    "fg_muted": "#7c8696",
    "border": "#3d4454",
    "accent": "#5b9fff",
    "accent_hover": "#7db0ff",
    "accent_pressed": "#3d7ad6",
    "on_accent": "#ffffff",
    "entry_bg": "#222831",
    "text_area_bg": "#15181f",
    "selectbackground": "#3d5280",
    "selectforeground": "#f2f6fc",
    "bg_button_active": "#353945",
    "bg_button_pressed": "#2a2f3a",
}

# Палитра по умолчанию для импорта и тестов (совпадает с темой по умолчанию).
PALETTE: dict[str, str] = dict(PALETTE_LIGHT)


def hex_foreground_darkened(root: tk.Misc, *, factor: float = 0.85) -> str | None:
    """
    Цвет подписи по умолчанию, затемнённый к чёрному (factor=0.85 ≈ на 15%).

    ``root`` — любой виджет с методом ``winfo_rgb`` (обычно ``Tk``).
    """
    probe = tk.Label(root)
    try:
        name = probe.cget("fg")
    finally:
        probe.destroy()
    try:
        r16, g16, b16 = root.winfo_rgb(name)
    except tk.TclError:
        return None
    r = max(0, min(255, int(r16 * factor // 256)))
    g = max(0, min(255, int(g16 * factor // 256)))
    b = max(0, min(255, int(b16 * factor // 256)))
    return f"#{r:02x}{g:02x}{b:02x}"


def hex_color_darkened(root: tk.Misc, color: str, *, factor: float = 0.85) -> str:
    """Затемнить именованный или hex-цвет; при ошибке вернуть ``color``."""
    try:
        r16, g16, b16 = root.winfo_rgb(color)
    except tk.TclError:
        return color
    r = max(0, min(255, int(r16 * factor // 256)))
    g = max(0, min(255, int(g16 * factor // 256)))
    b = max(0, min(255, int(b16 * factor // 256)))
    return f"#{r:02x}{g:02x}{b:02x}"


def _srgb_channel_to_linear(c: int) -> float:
    x = max(0, min(255, c)) / 255.0
    return x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4


def relative_luminance_hex(hex_color: str) -> float:
    """Относительная яркость sRGB ``#rrggbb`` в диапазоне ~0…1."""
    h = (hex_color or "").strip().lstrip("#")
    if len(h) != 6:
        return 0.5
    try:
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    except ValueError:
        return 0.5
    r_lin = _srgb_channel_to_linear(r)
    g_lin = _srgb_channel_to_linear(g)
    b_lin = _srgb_channel_to_linear(b)
    return 0.2126 * r_lin + 0.7152 * g_lin + 0.0722 * b_lin


def voice_status_text_font() -> tuple[str, int, str]:
    """
    Жирный шрифт +2 pt к TkDefaultFont: статус урока, «Результат», текст «Задание».
    """
    base = tkfont.nametofont("TkDefaultFont")
    fam = str(base.actual()["family"])
    sz = int(base.cget("size"))
    return (fam, max(6, sz + 2), "bold")


def contrast_select_foreground(select_background: str) -> str:
    """
    Цвет текста выделения: тёмный на светлой полосе, светлый на тёмной.

    Устраняет сочетания вроде «светлый фон выделения + светлые буквы».
    """
    lum = relative_luminance_hex(select_background)
    return "#0f172a" if lum > 0.42 else "#f8fafc"


def apply_professional_theme(
    root: tk.Tk,
    *,
    variant: Literal["light", "dark"] = "light",
) -> None:
    """
    Тема «clam», палитра, стили кнопок/вкладок/рамок.

    ``variant``: ``"light"`` — светлая (по умолчанию), ``"dark"`` — тёмная.

    Вызывать после настройки размеров шрифтов; сохраняет ``_lang_learn_palette``,
    ``_lang_learn_fg_dark`` и ``_lang_learn_theme_variant`` на ``root``.
    """
    p: dict[str, str] = dict(
        PALETTE_LIGHT if variant == "light" else PALETTE_DARK,
    )
    sel_bg = p["selectbackground"]
    p["selectforeground"] = contrast_select_foreground(sel_bg)
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    base = tkfont.nametofont("TkDefaultFont")
    fam = base.actual()["family"]
    sz = base.cget("size")
    bold_title = (fam, sz, "bold")

    # Корневой фон окна — ключ bg_app.
    root.configure(bg=p["bg_app"])
    setattr(root, "_lang_learn_palette", dict(p))
    setattr(root, "_lang_learn_fg_dark", p["fg"])
    setattr(root, "_lang_learn_theme_variant", variant)

    # Три оттенка зон окна; при отсутствии ключей — bg_elevated / bg_card.
    session_bg = p.get("bg_section_params", p["bg_elevated"])
    content_bg = p.get("bg_section_content", p["bg_card"])
    progress_bg = p.get("bg_section_progress", p["bg_elevated"])

    style.configure("App.TFrame", background=p["bg_app"])
    style.configure("Content.TFrame", background=content_bg)
    style.configure("Card.TFrame", background=content_bg)
    style.configure("TFrame", background=p["bg_app"])

    # Panel — запасной стиль «как зона параметров» (совместимость).
    style.configure("Panel.TFrame", background=session_bg)
    style.configure("OnCard.TFrame", background=content_bg)

    # Session — блок «Параметры сессии» (desktop_chat).
    style.configure(
        "Session.TLabelframe",
        background=session_bg,
        foreground=p["fg"],
        borderwidth=0,
        relief="flat",
    )
    style.configure(
        "Session.TLabelframe.Label",
        background=session_bg,
        foreground=p["fg"],
        font=bold_title,
    )
    style.configure(
        "Session.TLabel",
        background=session_bg,
        foreground=p["fg"],
        font=base,
    )

    # Progress — блок «Прогресс» (desktop_chat).
    style.configure(
        "Progress.TLabelframe",
        background=progress_bg,
        foreground=p["fg"],
        borderwidth=0,
        relief="flat",
    )
    style.configure(
        "Progress.TLabelframe.Label",
        background=progress_bg,
        foreground=p["fg"],
        font=bold_title,
    )

    # Рамки с подписью: borderwidth=0 — без видимой границы (минималистичный вид).
    style.configure(
        "Panel.TLabelframe",
        background=session_bg,
        foreground=p["fg"],
        borderwidth=0,
        relief="flat",
    )
    style.configure(
        "Panel.TLabelframe.Label",
        background=session_bg,
        foreground=p["fg"],
        font=bold_title,
    )
    style.configure(
        "Panel.TLabel",
        background=session_bg,
        foreground=p["fg"],
        font=base,
    )

    style.configure(
        "OnCard.TLabelframe",
        background=content_bg,
        foreground=p["fg"],
        borderwidth=0,
        relief="flat",
    )
    style.configure(
        "OnCard.TLabelframe.Label",
        background=content_bg,
        foreground=p["fg"],
        font=bold_title,
    )
    # Рамка «Задание» урока: подпись +2 pt к базовому кеглю, жирный.
    style.configure(
        "LessonTask.TLabelframe",
        background=content_bg,
        foreground=p["fg"],
        borderwidth=0,
        relief="flat",
    )
    style.configure(
        "LessonTask.TLabelframe.Label",
        background=content_bg,
        foreground=p["fg"],
        font=voice_status_text_font(),
    )
    style.configure(
        "OnCard.TLabel",
        background=content_bg,
        foreground=p["fg"],
        font=base,
    )
    # Статус урока алфавита у кнопки «Озвучить эталон»: +2 pt к базовому кеглю, жирный.
    style.configure(
        "VoiceStatus.TLabel",
        background=content_bg,
        foreground=p["fg"],
        font=voice_status_text_font(),
    )
    # Заголовок урока: max(sz, 9) — не ниже 9 pt относительно базового sz.
    style.configure(
        "Title.TLabel",
        background=p["bg_card"],
        foreground=p["fg"],
        font=(fam, max(sz, 9), "bold"),
    )
    style.configure(
        "Hint.TLabel",
        background=p["bg_card"],
        foreground=p["fg_muted"],
        font=base,
    )

    style.configure("TLabel", background=p["bg_app"], foreground=p["fg"], font=base)
    style.configure(
        "TEntry",
        fieldbackground=p["entry_bg"],
        foreground=p["fg"],
        insertcolor=p["fg"],
    )
    style.map(
        "TEntry",
        selectbackground=[("!disabled", sel_bg)],
        selectforeground=[("!disabled", p["selectforeground"])],
    )
    style.configure(
        "TCombobox",
        fieldbackground=p["entry_bg"],
        foreground=p["fg"],
        arrowcolor=p["fg_secondary"],
    )
    combo_sel_bg = p["accent"]
    combo_sel_fg = contrast_select_foreground(combo_sel_bg)
    style.map(
        "TCombobox",
        fieldbackground=[("readonly", p["entry_bg"])],
        selectbackground=[
            ("readonly", combo_sel_bg),
            ("!disabled", sel_bg),
        ],
        selectforeground=[
            ("readonly", combo_sel_fg),
            ("!disabled", p["selectforeground"]),
        ],
    )

    style.configure("TNotebook", background=content_bg, borderwidth=0)
    # Вкладки: padding (гориз., верт.) — отступ текста и «высота» вкладки.
    style.configure(
        "TNotebook.Tab",
        background=p["bg_tab"],
        foreground=p["fg_muted"],
        padding=(6, 3),
        font=base,
        borderwidth=0,
    )
    style.map(
        "TNotebook.Tab",
        background=[("selected", p["bg_app"])],
        foreground=[("selected", p["fg"])],
    )

    # Обычная кнопка: padding (гориз., верт.).
    style.configure(
        "TButton",
        background=p["bg_panel"],
        foreground=p["fg"],
        padding=(5, 3),
        font=base,
    )
    style.map(
        "TButton",
        background=[
            ("active", p["bg_button_active"]),
            ("pressed", p["bg_button_pressed"]),
        ],
    )

    # Акцентная кнопка (например «Отправить», «Проверить»).
    style.configure(
        "Accent.TButton",
        background=p["accent"],
        foreground=p["on_accent"],
        padding=(6, 4),
        font=base,
    )
    style.map(
        "Accent.TButton",
        background=[
            ("active", p["accent_hover"]),
            ("pressed", p["accent_pressed"]),
        ],
        foreground=[("active", p["on_accent"]), ("pressed", p["on_accent"])],
    )

    style.configure(
        "Muted.TButton",
        background=p["bg_elevated"],
        foreground=p["fg"],
        padding=(5, 3),
        font=base,
    )
    style.map(
        "Muted.TButton",
        background=[
            ("active", p["bg_button_active"]),
            ("pressed", p["bg_button_pressed"]),
        ],
    )

    # Согласование цветов классических виджетов (не ttk) с палитрой.
    fg = p["fg"]
    root.option_add("*Foreground", fg)
    root.option_add("*Text.foreground", fg)
    root.option_add("*Entry.foreground", fg)
    root.option_add("*Listbox.foreground", fg)
    root.option_add("*Menubutton.foreground", fg)
    root.option_add("*Menu.foreground", fg)
    root.option_add("*Entry.selectBackground", sel_bg)
    root.option_add("*Entry.selectForeground", p["selectforeground"])
    root.option_add("*Text.selectBackground", sel_bg)
    root.option_add("*Text.selectForeground", p["selectforeground"])
    root.option_add("*Listbox.selectBackground", sel_bg)
    root.option_add("*Listbox.selectForeground", p["selectforeground"])
    try:
        root.configure(fg=fg)
    except tk.TclError:
        pass


def style_text_widget(
    w: tk.Misc,
    pal: Mapping[str, str],
    *,
    font: tuple[str, int, str] | tkfont.Font | None = None,
) -> None:
    """
    Оформление ``Text`` / ``ScrolledText``: фон, цвет текста, выделение.

    Использует ключи палитры ``text_area_bg``, ``fg``, ``select*``;
    ``highlightthickness=0`` — без рамки фокуса вокруг поля.

    ``font``: при задании подставляется в ``configure`` (например
    ``voice_status_text_font()`` для текста как у статуса урока).
    """
    sel_bg = pal.get("selectbackground", pal["bg_tab"])
    sel_fg = contrast_select_foreground(sel_bg)
    cfg: dict[str, object] = {
        "foreground": pal["fg"],
        "background": pal["text_area_bg"],
        "insertbackground": pal["fg"],
        "selectbackground": sel_bg,
        "selectforeground": sel_fg,
        "highlightthickness": 0,
        "highlightbackground": pal["bg_card"],
        "highlightcolor": pal["fg"],
        "relief": tk.FLAT,
        "borderwidth": 0,
    }
    if font is not None:
        cfg["font"] = font
    w.configure(**cfg)
