"""Пути к каталогу данных и схеме БД."""

from __future__ import annotations

import sys
from pathlib import Path

from lang_learn.persistence.app_paths import (
    default_app_data_dir,
    default_progress_database_path,
    repository_schema_sql_path,
)


def test_repository_schema_sql_path_exists() -> None:
    p = repository_schema_sql_path()
    assert p.name == "schema.sql"
    assert p.parent.name == "db"
    assert p.is_file()


def test_default_progress_database_path_under_app_dir() -> None:
    db = default_progress_database_path()
    assert db.name == "progress.db"
    assert db.parent == default_app_data_dir()


def test_default_app_data_dir_windows(monkeypatch) -> None:
    monkeypatch.setenv("LOCALAPPDATA", r"C:\Users\Test\AppData\Local")
    monkeypatch.setattr(sys, "platform", "win32")
    assert default_app_data_dir() == Path(r"C:\Users\Test\AppData\Local") / "lang_learn"


def test_default_app_data_dir_xdg(monkeypatch) -> None:
    monkeypatch.delenv("LOCALAPPDATA", raising=False)
    monkeypatch.setenv("XDG_DATA_HOME", "/home/u/.local/share")
    monkeypatch.setattr(sys, "platform", "linux")
    assert default_app_data_dir() == Path("/home/u/.local/share/lang_learn")


def test_default_app_data_dir_linux_fallback_home(monkeypatch) -> None:
    monkeypatch.delenv("LOCALAPPDATA", raising=False)
    monkeypatch.delenv("XDG_DATA_HOME", raising=False)
    monkeypatch.setattr(sys, "platform", "linux")
    assert default_app_data_dir() == Path.home() / ".local" / "share" / "lang_learn"
