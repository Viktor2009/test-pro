"""Накопление истории реплик для ``DialogSessionContext`` (этап 8, без tkinter)."""

from __future__ import annotations

from lang_learn.schemas.llm import ChatMessage, ChatRole


def append_turn_to_history(
    prior: tuple[ChatMessage, ...],
    *,
    user_text: str,
    assistant_reply: str,
) -> tuple[ChatMessage, ...]:
    """Добавить пару user/assistant после одного успешного хода."""
    return (
        *prior,
        ChatMessage(role=ChatRole.USER, content=user_text),
        ChatMessage(role=ChatRole.ASSISTANT, content=assistant_reply),
    )
