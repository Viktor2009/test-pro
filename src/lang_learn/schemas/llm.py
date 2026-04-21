"""Схемы для LLM Gateway (этап 3+); минимальный каркас для контракта."""

from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from lang_learn.schemas.common import LanguageCode


class ChatRole(str, Enum):
    """Роль сообщения в диалоге."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class ChatMessage(BaseModel):
    """Одно сообщение в истории чата."""

    model_config = ConfigDict(frozen=True)

    role: ChatRole
    content: str = Field(min_length=1)


class LLMProviderConfig(BaseModel):
    """Параметры вызова провайдера (модель, температура и т.д.)."""

    model_config = ConfigDict(frozen=True)

    model: str = Field(min_length=1)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int | None = Field(default=None, ge=1, le=128000)
    response_format_json: bool = False


class LLMRequest(BaseModel):
    """Запрос к LLM: сообщения и настройки."""

    model_config = ConfigDict(frozen=True)

    messages: tuple[ChatMessage, ...] = Field(min_length=1)
    target_language: LanguageCode | None = None
    config: LLMProviderConfig


class LLMResult(BaseModel):
    """Сырой ответ провайдера (парсинг JSON — на слое оркестрации)."""

    model_config = ConfigDict(frozen=True)

    text: str = Field(min_length=1)
    finish_reason: Literal["stop", "length", "content_filter", "other"] = "stop"
    raw: dict[str, object] | None = None
