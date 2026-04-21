"""Локальные настройки GUI (JSON рядом с каталогом данных приложения)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from lang_learn.persistence.app_paths import default_app_data_dir

PREFS_FILENAME = "gui_preferences.json"
KEY_LLM_PROVIDER = "llm_provider"


def gui_preferences_path() -> Path:
    """Файл ``gui_preferences.json`` в ``default_app_data_dir()``."""
    return default_app_data_dir() / PREFS_FILENAME


def load_gui_preferences() -> dict[str, Any]:
    """Прочитать JSON-настройки; при отсутствии или ошибке — пустой dict."""
    path = gui_preferences_path()
    if not path.is_file():
        return {}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return {}
    return raw if isinstance(raw, dict) else {}


def save_gui_preferences(prefs: dict[str, Any]) -> None:
    """Атомарно перезаписать файл настроек (родительский каталог создаётся)."""
    path = gui_preferences_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(prefs, ensure_ascii=False, indent=2) + "\n"
    path.write_text(text, encoding="utf-8")


def read_llm_provider_choice() -> str | None:
    """Последний выбранный LLM (ключ реестра) или ``None``."""
    prefs = load_gui_preferences()
    v = prefs.get(KEY_LLM_PROVIDER)
    return str(v).strip().lower() if isinstance(v, str) and v.strip() else None


def write_llm_provider_choice(name: str) -> None:
    """Сохранить ключ LLM-провайдера."""
    key = name.strip().lower()
    prefs = load_gui_preferences()
    prefs[KEY_LLM_PROVIDER] = key
    save_gui_preferences(prefs)


def resolve_initial_llm_provider(
    available: tuple[str, ...],
    *,
    stored: str | None,
) -> str:
    """Выбрать стартовое имя провайдера из списка реестра и сохранённого значения."""
    if not available:
        return "stub"
    allowed = frozenset(x.lower() for x in available)
    if stored and stored.strip().lower() in allowed:
        return stored.strip().lower()
    return available[0]
