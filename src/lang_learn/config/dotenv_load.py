"""Загрузка переменных окружения из файлов ``.env`` при старте приложения."""

from __future__ import annotations

import os
from pathlib import Path

_LOADED = False


def _truthy_skip_dotenv() -> bool:
    v = (os.environ.get("LANG_LEARN_SKIP_DOTENV") or "").strip().lower()
    return v in ("1", "true", "yes", "on")


def load_dotenv_files() -> None:
    """
    Прочитать ``.env`` в ``os.environ`` (идемпотентно).

    Порядок файлов:

    1. ``%LOCALAPPDATA%/lang_learn/.env`` (или XDG-аналог) — постоянное место
       для пользовательской установки;
    2. ``.env`` в текущем рабочем каталоге — перекрывает те же ключи из шага 1
       (удобно для разработки из клона репозитория).

    Уже заданные в среде ОС переменные при первом файле не перезаписываются;
    второй файл перезаписывает только ключи, присутствующие в нём самом
    (включая значения из первого ``.env``).

    Отключение (тесты, CI): ``LANG_LEARN_SKIP_DOTENV=1``.
    """
    global _LOADED
    if _LOADED:
        return
    _LOADED = True
    if _truthy_skip_dotenv():
        return

    try:
        from dotenv import load_dotenv
    except ImportError:
        return

    from lang_learn.persistence.app_paths import default_app_data_dir

    app_env = default_app_data_dir() / ".env"
    cwd_env = Path.cwd() / ".env"

    if app_env.is_file():
        load_dotenv(app_env, override=False)
    if cwd_env.is_file():
        load_dotenv(cwd_env, override=True)
