"""Адаптеры хранения прогресса (SQLite, in-memory для тестов)."""

from lang_learn.persistence.app_paths import (
    default_app_data_dir,
    default_progress_database_path,
    repository_schema_sql_path,
)
from lang_learn.persistence.memory_progress import MemoryProgressRepository
from lang_learn.persistence.sqlite_progress import SqliteProgressRepository

__all__ = [
    "MemoryProgressRepository",
    "SqliteProgressRepository",
    "default_app_data_dir",
    "default_progress_database_path",
    "repository_schema_sql_path",
]
