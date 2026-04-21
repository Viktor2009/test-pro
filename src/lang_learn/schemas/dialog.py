"""Структурированный ответ ИИ в диалоге (этап 3)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from lang_learn.schemas.audio import AudioFormat
from lang_learn.schemas.common import LanguageCode
from lang_learn.schemas.llm import ChatMessage

NextDialogAction = Literal[
    "continue",
    "ask_user_to_repeat",
    "summarize",
    "end_session",
]


class CorrectionItem(BaseModel):
    """Правка формулировки ученика."""

    model_config = ConfigDict(frozen=True)

    original_fragment: str = ""
    suggested: str = ""
    explanation: str = ""


class VocabularyItem(BaseModel):
    """Новая лексика из реплики ассистента."""

    model_config = ConfigDict(frozen=True)

    term: str = Field(min_length=1, max_length=128)
    gloss: str = Field(default="", max_length=256)


class StructuredDialogResponse(BaseModel):
    """
    Жёсткий JSON-формат ответа модели в учебном диалоге.

    Поля согласованы с планом: assistant_reply, corrections,
    new_vocabulary, next_action.
    """

    model_config = ConfigDict(frozen=True)

    assistant_reply: str = Field(min_length=1, max_length=8000)
    corrections: tuple[CorrectionItem, ...] = ()
    new_vocabulary: tuple[VocabularyItem, ...] = ()
    next_action: NextDialogAction = "continue"


class DialogSessionContext(BaseModel):
    """Контекст одного хода: тема, цель, уровень, последняя реплика ученика."""

    model_config = ConfigDict(frozen=True)

    topic: str = Field(min_length=1, max_length=256)
    session_goal: str = Field(
        min_length=1,
        max_length=4096,
        description="Цель сессии; travel-сценарии могут задавать длинный контекст.",
    )
    level_hint: str = Field(
        default="A1",
        max_length=32,
        description="Подсказка уровня CEFR или pre_a0.",
    )
    target_language: LanguageCode
    user_latest_message: str = Field(min_length=1, max_length=4000)
    max_reply_sentences: int = Field(default=3, ge=1, le=12)
    prior_messages: tuple[ChatMessage, ...] = ()


class DialogTurnResult(BaseModel):
    """Итог хода: валидированный JSON, сырой ответ LLM, флаг fallback, опц. TTS."""

    model_config = ConfigDict(frozen=True)

    structured: StructuredDialogResponse
    fallback_used: bool
    raw_text: str = Field(description="Сырой текст от провайдера LLM.")
    tts_audio: bytes | None = None
    tts_format: AudioFormat | None = None
