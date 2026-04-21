"""Пути к данным приложения на диске (GUI, локальный прогресс)."""

from __future__ import annotations

import os
import sys
from pathlib import Path


def repository_schema_sql_path() -> Path:
    """
    Путь к ``db/schema.sql`` в корне репозитория (каталог рядом с ``src``).

    Ожидается раскладка: ``<repo>/src/lang_learn/persistence/app_paths.py``.
    """
    # .../src/lang_learn/persistence/app_paths.py -> parents[2] == src
    src = Path(__file__).resolve().parents[2]
    return src.parent / "db" / "schema.sql"


def default_app_data_dir() -> Path:
    """
    Каталог пользовательских данных приложения (создавать через ``mkdir``).

    Windows: ``%LOCALAPPDATA%\\lang_learn``;
    иначе: ``$XDG_DATA_HOME/lang_learn`` или ``~/.local/share/lang_learn``.
    """
    if sys.platform == "win32":
        local = os.environ.get("LOCALAPPDATA")
        if local:
            return Path(local) / "lang_learn"
    xdg = os.environ.get("XDG_DATA_HOME")
    if xdg:
        return Path(xdg) / "lang_learn"
    return Path.home() / ".local" / "share" / "lang_learn"


def default_progress_database_path() -> Path:
    """Файл SQLite прогресса по умолчанию для GUI."""
    return default_app_data_dir() / "progress.db"
