"""
Черновые DTO для внешнего REST/интеграции (этап 7).

Слой не выполняет HTTP; только структуры запрос/ответ, согласованные с
``DialogOrchestrator`` / ``DialogSessionContext``.
"""

from __future__ import annotations

from typing import Any, cast

from pydantic import BaseModel, ConfigDict, Field

from lang_learn.schemas.common import LanguageCode
from lang_learn.schemas.dialog import (
    DialogSessionContext,
    DialogTurnResult,
    StructuredDialogResponse,
)


class HttpDialogTurnRequest(BaseModel):
    """
    Тело запроса «один ход диалога» для внешнего API.

    ``llm_provider`` — ключ из ``ProviderRegistry`` (например ``stub``).
    """

    model_config = ConfigDict(frozen=True)

    topic: str = Field(min_length=1, max_length=256)
    session_goal: str = Field(min_length=1, max_length=4096)
    level_hint: str = Field(default="A1", max_length=32)
    target_language: str = Field(min_length=2, max_length=32)
    user_latest_message: str = Field(min_length=1, max_length=4000)
    max_reply_sentences: int = Field(default=3, ge=1, le=12)
    llm_provider: str = Field(default="stub", min_length=1, max_length=64)
    user_scope: dict[str, Any] | None = Field(
        default=None,
        description='Опционально: {"external_user_id": "…", "tenant_id": …}',
    )

    def to_session_context(self) -> DialogSessionContext:
        """Собрать доменный контекст для оркестратора."""
        return DialogSessionContext(
            topic=self.topic,
            session_goal=self.session_goal,
            level_hint=self.level_hint,
            target_language=cast(LanguageCode, self.target_language),
            user_latest_message=self.user_latest_message,
            max_reply_sentences=self.max_reply_sentences,
        )


class HttpDialogTurnResponse(BaseModel):
    """Плоский ответ API после одного хода (без сырых байтов TTS)."""

    model_config = ConfigDict(frozen=True)

    structured: StructuredDialogResponse
    fallback_used: bool
    raw_text: str = Field(description="Сырой ответ LLM (для отладки интеграции).")
    has_tts_audio: bool = Field(
        default=False,
        description="True, если в доменном результате было аудио TTS.",
    )

    @classmethod
    def from_turn_result(cls, result: DialogTurnResult) -> HttpDialogTurnResponse:
        return cls(
            structured=result.structured,
            fallback_used=result.fallback_used,
            raw_text=result.raw_text,
            has_tts_audio=result.tts_audio is not None,
        )
