"""DTO строк БД согласованы с ожидаемыми полями."""

from lang_learn.schemas.persistence import AttemptRow, UserRow


def test_user_row() -> None:
    row = UserRow(id=1, created_utc="2026-01-01T00:00:00Z", display_name="u1")
    assert row.display_name == "u1"


def test_attempt_row_errors_default() -> None:
    row = AttemptRow(
        id=1,
        user_id=1,
        exercise_id="ex-1",
        created_utc="2026-01-01T00:00:00Z",
    )
    assert row.errors == []
