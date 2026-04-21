"""Модели курса Pre-A0 (буквы, сочетания, минимальные пары)."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from lang_learn.schemas.common import LanguageCode


class ExerciseKind(str, Enum):
    """Типы упражнений этапа 2 (MVP-движок)."""

    LISTEN_REPEAT = "listen_repeat"
    READ_ALOUD_COMPARE = "read_aloud_compare"
    RECOGNIZE_LETTER = "recognize_letter"


class LetterEntry(BaseModel):
    """Одна буква (графема) и опорное слово."""

    model_config = ConfigDict(frozen=True)

    id: str = Field(min_length=1, pattern=r"^[a-z0-9._-]+$")
    grapheme: str = Field(min_length=1, max_length=8)
    ipa: str = ""
    example_word: str = Field(min_length=1, max_length=64)


class ClusterEntry(BaseModel):
    """Частое буквосочетание (диграф / кластер)."""

    model_config = ConfigDict(frozen=True)

    id: str = Field(min_length=1, pattern=r"^[a-z0-9._-]+$")
    grapheme: str = Field(min_length=1, max_length=16)
    ipa: str = ""
    example_word: str = Field(min_length=1, max_length=64)


class MinimalPairEntry(BaseModel):
    """Минимальная пара слов (различие одного признака)."""

    model_config = ConfigDict(frozen=True)

    id: str = Field(min_length=1, pattern=r"^[a-z0-9._-]+$")
    word_a: str = Field(min_length=1, max_length=64)
    word_b: str = Field(min_length=1, max_length=64)
    focus: str = Field(default="", max_length=128)


class PreA0Course(BaseModel):
    """Описание курса Pre-A0 (загрузка из JSON)."""

    model_config = ConfigDict(frozen=True)

    version: int = Field(default=1, ge=1)
    language: LanguageCode
    title: str = Field(default="Pre-A0", max_length=256)
    letters: tuple[LetterEntry, ...] = ()
    clusters: tuple[ClusterEntry, ...] = ()
    minimal_pairs: tuple[MinimalPairEntry, ...] = ()
