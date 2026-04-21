"""Сценарии «путешествия»: лексика, фразы, вариации, карточка выживания."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from lang_learn.schemas.common import LanguageCode


class TravelLexeme(BaseModel):
    """Активный минимум (термин + краткий перевод)."""

    model_config = ConfigDict(frozen=True)

    term: str = Field(min_length=1, max_length=128)
    gloss: str = Field(default="", max_length=256)


class TravelPhrase(BaseModel):
    """Обязательная фраза-шаблон; ``survival`` — в карточку выживания."""

    model_config = ConfigDict(frozen=True)

    id: str = Field(min_length=1, max_length=64, pattern=r"^[a-z0-9._-]+$")
    text: str = Field(min_length=1, max_length=512)
    gloss: str = Field(default="", max_length=512)
    survival: bool = False


class ScenarioVariation(BaseModel):
    """Уровень вариации ситуации (1 — проще, выше — сложнее / больше отвлечений)."""

    model_config = ConfigDict(frozen=True)

    level: int = Field(ge=1, le=5)
    title: str = Field(min_length=1, max_length=256)
    coach_note: str = Field(default="", max_length=1024)
    clarifying_questions: tuple[str, ...] = ()


class TravelScenario(BaseModel):
    """Один тематический сценарий (аэропорт, отель, …)."""

    model_config = ConfigDict(frozen=True)

    slug: str = Field(min_length=2, max_length=64, pattern=r"^[a-z][a-z0-9-]*$")
    title: str = Field(min_length=1, max_length=256)
    target_language: LanguageCode
    lexicon: tuple[TravelLexeme, ...] = ()
    phrases: tuple[TravelPhrase, ...] = ()
    variations: tuple[ScenarioVariation, ...] = ()


class TravelScenarioBundle(BaseModel):
    """Набор сценариев из одного JSON."""

    model_config = ConfigDict(frozen=True)

    version: int = Field(default=1, ge=1)
    scenarios: tuple[TravelScenario, ...] = Field(min_length=1)
