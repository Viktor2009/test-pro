"""Сборка системного промпта и истории для учебного диалога."""

from __future__ import annotations

from lang_learn.schemas.dialog import DialogSessionContext
from lang_learn.schemas.llm import ChatMessage, ChatRole


def _json_contract_block() -> str:
    return (
        "Ответь СТРОГО одним JSON-объектом без Markdown и без пояснений до/после. "
        "Схема полей:\n"
        '- "assistant_reply": string — короткая реплика ассистента на целевом языке;\n'
        '- "corrections": массив объектов '
        '{"original_fragment","suggested","explanation"} (можно []);\n'
        '- "new_vocabulary": массив объектов {"term","gloss"} (можно []);\n'
        '- "next_action": один из строк '
        '"continue"|"ask_user_to_repeat"|"summarize"|"end_session".'
    )


def build_dialog_messages(ctx: DialogSessionContext) -> tuple[ChatMessage, ...]:
    """
    Собрать сообщения для ``LLMRequest``: системный промпт + история + реплика.

    Системный промпт задаёт роль учебного собеседника, тему, уровень и лимиты.
    """
    system_lines = [
        "Ты учебный собеседник для изучения иностранного языка.",
        f"Тема сессии: {ctx.topic}.",
        f"Цель сессии: {ctx.session_goal}.",
        f"Уровень ученика (ориентир): {ctx.level_hint}.",
        f"Целевой язык общения (BCP-47): {ctx.target_language}.",
        f"Держи ответ ассистента не длиннее примерно {ctx.max_reply_sentences} "
        "коротких предложений.",
        "Будь доброжелательным, корректируй ошибки мягко, избегай лишней лексики "
        "выше уровня.",
        "",
        _json_contract_block(),
    ]
    system = "\n".join(system_lines)
    out: list[ChatMessage] = [
        ChatMessage(role=ChatRole.SYSTEM, content=system),
        *ctx.prior_messages,
        ChatMessage(role=ChatRole.USER, content=ctx.user_latest_message),
    ]
    return tuple(out)
