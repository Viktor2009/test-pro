"""Нормализация идентификатора пользователя сессии GUI."""

from lang_learn.gui.desktop_chat import normalize_session_user_id


def test_normalize_session_user_id_empty() -> None:
    assert normalize_session_user_id("") == "gui-user"
    assert normalize_session_user_id("   ") == "gui-user"


def test_normalize_session_user_id_trim() -> None:
    assert normalize_session_user_id("  alice  ") == "alice"


def test_normalize_session_user_id_max_length() -> None:
    long_id = "x" * 200
    assert len(normalize_session_user_id(long_id)) == 128
