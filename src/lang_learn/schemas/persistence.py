"""
Черновые DTO под строки БД (SQLite), согласованные с `db/schema.sql`.

Используются для типизации репозиториев; сериализация JSON — на слое хранения.
"""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from lang_learn.schemas.common import LanguageCode


class UserRow(BaseModel):
    """Строка `users`."""

    model_config = ConfigDict(frozen=True)

    id: int = Field(ge=1)
    created_utc: str
    display_name: str | None = None


class LearningProfileRow(BaseModel):
    """Строка `learning_profiles`."""

    model_config = ConfigDict(frozen=True)

    id: int = Field(ge=1)
    user_id: int = Field(ge=1)
    interface_language: LanguageCode | None = None
    target_language: LanguageCode
    level_hint: str | None = None
    updated_utc: str


class ScenarioRow(BaseModel):
    """Строка `scenarios`."""

    model_config = ConfigDict(frozen=True)

    id: int = Field(ge=1)
    slug: str = Field(min_length=1)
    title: str = Field(min_length=1)
    description: str | None = None
    theme: str = Field(min_length=1)


class LessonRow(BaseModel):
    """Строка `lessons`."""

    model_config = ConfigDict(frozen=True)

    id: int = Field(ge=1)
    scenario_id: int | None = Field(default=None, ge=1)
    title: str = Field(min_length=1)
    sort_order: int = 0
    metadata: dict[str, Any] = Field(default_factory=dict)


class AttemptRow(BaseModel):
    """Строка `attempts` (ключевые поля из плана: тема, навык, транскрипт, ошибки)."""

    model_config = ConfigDict(frozen=True)

    id: int = Field(ge=1)
    user_id: int = Field(ge=1)
    lesson_id: int | None = Field(default=None, ge=1)
    scenario_id: int | None = Field(default=None, ge=1)
    exercise_id: str = Field(min_length=1)
    target_skill: str | None = None
    reference_text: str | None = None
    stt_transcript: str | None = None
    errors: list[dict[str, Any]] = Field(default_factory=list)
    score: float | None = Field(default=None, ge=0.0, le=1.0)
    recommendation_next: str | None = None
    created_utc: str
    details: dict[str, Any] = Field(default_factory=dict)


class PronunciationReportRow(BaseModel):
    """Строка `pronunciation_reports`."""

    model_config = ConfigDict(frozen=True)

    id: int = Field(ge=1)
    attempt_id: int = Field(ge=1)
    report: dict[str, Any] = Field(default_factory=dict)
    created_utc: str


class ReviewQueueRow(BaseModel):
    """Строка `review_queue`."""

    model_config = ConfigDict(frozen=True)

    id: int = Field(ge=1)
    user_id: int = Field(ge=1)
    due_utc: str
    item_kind: str = Field(min_length=1)
    item_ref: str = Field(min_length=1)
    payload: dict[str, Any] = Field(default_factory=dict)


class SessionLogRow(BaseModel):
    """Строка `session_logs`."""

    model_config = ConfigDict(frozen=True)

    id: int = Field(ge=1)
    user_id: int = Field(ge=1)
    started_utc: str
    ended_utc: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
