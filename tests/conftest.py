"""Общие настройки pytest."""

from __future__ import annotations

import os


def pytest_configure() -> None:
    """Не подмешивать пользовательский ``.env`` в тесты по умолчанию."""
    os.environ.setdefault("LANG_LEARN_SKIP_DOTENV", "1")
