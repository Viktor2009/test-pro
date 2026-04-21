"""Настройки GUI: JSON и выбор LLM."""

from __future__ import annotations

from pathlib import Path

import pytest

from lang_learn.gui import preferences as prefs


def test_resolve_initial_llm_provider_prefers_stored() -> None:
    assert prefs.resolve_initial_llm_provider(("stub",), stored="stub") == "stub"


def test_resolve_initial_llm_provider_fallback() -> None:
    assert prefs.resolve_initial_llm_provider(("stub", "x"), stored="unknown") == "stub"


def test_read_write_llm_roundtrip(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(prefs, "gui_preferences_path", lambda: tmp_path / "gui.json")
    assert prefs.read_llm_provider_choice() is None
    prefs.write_llm_provider_choice("stub")
    assert prefs.read_llm_provider_choice() == "stub"


def test_load_gui_preferences_invalid_json(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    p = tmp_path / "bad.json"
    p.write_text("{not json", encoding="utf-8")
    monkeypatch.setattr(prefs, "gui_preferences_path", lambda: p)
    assert prefs.load_gui_preferences() == {}
