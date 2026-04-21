"""Сборка промпта для диалога."""

from lang_learn.learning.prompt_builder import build_dialog_messages
from lang_learn.schemas.dialog import DialogSessionContext


def test_build_dialog_messages_contains_topic_and_json_rules() -> None:
    ctx = DialogSessionContext(
        topic="Hotel",
        session_goal="Check-in phrases.",
        level_hint="A0",
        target_language="en-US",
        user_latest_message="I have a reservation.",
    )
    msgs = build_dialog_messages(ctx)
    assert msgs[0].role.value == "system"
    assert "Hotel" in msgs[0].content
    assert "assistant_reply" in msgs[0].content
    assert msgs[-1].role.value == "user"
    assert msgs[-1].content == "I have a reservation."
