"""Схемы для учебного движка и прогресса (этап 0+)."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from lang_learn.schemas.common import EntityId, LanguageCode


class LearningProfile(BaseModel):
    """Минимальный профиль обучения (расширяется на этапах 2–6)."""

    model_config = ConfigDict(frozen=True)

    user_id: EntityId
    interface_language: LanguageCode | None = None
    target_language: LanguageCode
    level_hint: str | None = Field(
        default=None,
        description="Например pre_a0, a0, a1 — без жёсткой схемы на раннем этапе.",
    )


class LessonContext(BaseModel):
    """Контекст для выбора следующего упражнения."""

    model_config = ConfigDict(frozen=True)

    user_id: EntityId
    scenario_id: EntityId | None = None
    lesson_id: EntityId | None = None
    extra: dict[str, Any] = Field(default_factory=dict)


class ExercisePayload(BaseModel):
    """Выдаваемое упражнение (заглушка структуры)."""

    model_config = ConfigDict(frozen=True)

    exercise_id: EntityId
    kind: str = Field(
        min_length=1,
        description="Тип упражнения, например repeat_after.",
    )
    instructions: str = ""
    reference_text: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class AttemptRecord(BaseModel):
    """Фиксация попытки пользователя."""

    model_config = ConfigDict(frozen=True)

    attempt_id: EntityId
    user_id: EntityId
    exercise_id: EntityId
    transcript: str | None = None
    score: float | None = Field(default=None, ge=0.0, le=1.0)
    created_at: datetime | None = None
    details: dict[str, Any] = Field(default_factory=dict)


class AttemptFeedback(BaseModel):
    """Краткий фидбек по попытке."""

    model_config = ConfigDict(frozen=True)

    accepted: bool
    summary: str = ""
    next_hint: str | None = None
