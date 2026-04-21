"""GUI: открытие SQLite-репозитория с подменой путей (без записи в профиль ОС)."""

from __future__ import annotations

from pathlib import Path

import pytest

from lang_learn.gui import desktop_chat
from lang_learn.schemas.learning import AttemptRecord, LearningProfile


@pytest.fixture
def patched_gui_repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    root = Path(__file__).resolve().parents[1]
    schema = root / "db" / "schema.sql"
    db = tmp_path / "gui_progress.sqlite"
    monkeypatch.setattr(
        desktop_chat,
        "repository_schema_sql_path",
        lambda: schema,
    )
    monkeypatch.setattr(
        desktop_chat,
        "default_progress_database_path",
        lambda: db,
    )
    repo = desktop_chat.open_gui_sqlite_progress_repository()
    try:
        yield repo
    finally:
        repo.close()


def test_open_gui_sqlite_progress_repository_creates_db(
    patched_gui_repo,
    tmp_path: Path,
) -> None:
    db = tmp_path / "gui_progress.sqlite"
    assert db.is_file()


def test_open_gui_sqlite_progress_profile_roundtrip(patched_gui_repo) -> None:
    r = patched_gui_repo
    r.save_profile(
        LearningProfile(
            user_id="gui-user",
            interface_language="ru-RU",
            target_language="en-GB",
            level_hint="a1",
        ),
    )
    loaded = r.load_profile("gui-user")
    assert loaded is not None
    assert loaded.target_language == "en-GB"
    assert loaded.level_hint == "a1"


def test_open_gui_sqlite_progress_attempt_survives_reopen(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = Path(__file__).resolve().parents[1]
    schema = root / "db" / "schema.sql"
    db = tmp_path / "persist.sqlite"
    monkeypatch.setattr(
        desktop_chat,
        "repository_schema_sql_path",
        lambda: schema,
    )
    monkeypatch.setattr(
        desktop_chat,
        "default_progress_database_path",
        lambda: db,
    )
    r1 = desktop_chat.open_gui_sqlite_progress_repository()
    try:
        r1.save_attempt(
            AttemptRecord(
                attempt_id="t1",
                user_id="gui-user",
                exercise_id="ex-x",
                transcript="hello",
                score=0.5,
                details={"skill_axis": "lexicon"},
            ),
        )
    finally:
        r1.close()
    r2 = desktop_chat.open_gui_sqlite_progress_repository()
    try:
        rows = r2.list_attempts("gui-user", limit=5)
        assert len(rows) >= 1
        assert any(x.exercise_id == "ex-x" for x in rows)
    finally:
        r2.close()
