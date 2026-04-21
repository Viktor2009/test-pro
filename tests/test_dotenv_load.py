"""Загрузка ``.env``."""

from __future__ import annotations

import importlib
import os
from pathlib import Path

import pytest


@pytest.fixture
def reset_dotenv_loader(monkeypatch: pytest.MonkeyPatch) -> None:
    import lang_learn.config.dotenv_load as m

    monkeypatch.setattr(m, "_LOADED", False)


def test_load_dotenv_respects_skip(
    reset_dotenv_loader,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    key = "LANG_LEARN_DOTENV_TEST_DUMMY"
    monkeypatch.setenv("LANG_LEARN_SKIP_DOTENV", "1")
    monkeypatch.chdir(tmp_path)
    p = tmp_path / ".env"
    p.write_text(f"{key}=should-not-load\n", encoding="utf-8")

    import lang_learn.config.dotenv_load as dl

    importlib.reload(dl)
    dl.load_dotenv_files()
    assert os.environ.get(key) != "should-not-load"


def test_load_dotenv_cwd_overrides_appdata(
    reset_dotenv_loader,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    key = "LANG_LEARN_DOTENV_TEST_DUMMY"
    monkeypatch.delenv("LANG_LEARN_SKIP_DOTENV", raising=False)
    monkeypatch.delenv(key, raising=False)

    app_dir = tmp_path / "appdata"
    monkeypatch.setattr(
        "lang_learn.persistence.app_paths.default_app_data_dir",
        lambda: app_dir,
    )
    app_dir.mkdir(parents=True, exist_ok=True)
    (app_dir / ".env").write_text(
        f"{key}=from-appdata\n",
        encoding="utf-8",
    )
    cwd = tmp_path / "proj"
    cwd.mkdir(parents=True, exist_ok=True)
    (cwd / ".env").write_text(
        f"{key}=from-cwd\n",
        encoding="utf-8",
    )
    monkeypatch.chdir(cwd)

    import lang_learn.config.dotenv_load as dl

    importlib.reload(dl)
    dl.load_dotenv_files()
    try:
        assert os.environ.get(key) == "from-cwd"
    finally:
        os.environ.pop(key, None)
