"""Этап 8: история диалога без tkinter."""

from lang_learn.gui.desktop_chat import _overview_lines
from lang_learn.gui.history import append_turn_to_history
from lang_learn.learning.progress_report import compute_progress_overview
from lang_learn.schemas.llm import ChatMessage, ChatRole


def test_append_turn_to_history() -> None:
    prior: tuple[ChatMessage, ...] = ()
    nxt = append_turn_to_history(
        prior,
        user_text="Hi",
        assistant_reply="Hello!",
    )
    assert len(nxt) == 2
    assert nxt[0].role == ChatRole.USER
    assert nxt[1].role == ChatRole.ASSISTANT
    again = append_turn_to_history(
        nxt,
        user_text="Bye",
        assistant_reply="Goodbye.",
    )
    assert len(again) == 4


def test_overview_lines_from_progress_overview() -> None:
    overview = compute_progress_overview(())
    text = _overview_lines(overview.model_dump_json())
    assert "KPI" in text
    assert "Готовность к поездке" in text
