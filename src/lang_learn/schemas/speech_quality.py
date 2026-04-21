"""
Оценка произношения и качество речи (этап 5).

MVP: текст и опционально длительности записей (мс).
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class PronunciationScores(BaseModel):
    """Сводные метрики в диапазоне ``[0, 1]``."""

    model_config = ConfigDict(frozen=True)

    intelligibility: float = Field(ge=0.0, le=1.0)
    word_accuracy: float = Field(ge=0.0, le=1.0)
    fluency: float = Field(ge=0.0, le=1.0)
    composite: float = Field(ge=0.0, le=1.0)


class WordAlignmentIssue(BaseModel):
    """Слово из эталона, которое плохо совпало с распознанным текстом."""

    model_config = ConfigDict(frozen=True)

    reference_word: str = Field(min_length=1, max_length=64)
    observed: str | None = Field(default=None, max_length=64)
    hint: str = Field(default="", max_length=512)


class PronunciationReport(BaseModel):
    """Отчёт для фидбека и трекинга: текст + оценки + подсказки."""

    model_config = ConfigDict(frozen=True)

    reference_text: str = Field(min_length=1)
    hypothesis_text: str = Field(default="", max_length=8000)
    scores: PronunciationScores
    word_issues: tuple[WordAlignmentIssue, ...] = ()
    articulation_tips: tuple[str, ...] = ()
    reference_echo_text: str = Field(
        default="",
        description="Текст эталона для повторения (озвучка — через TTS отдельно).",
    )


class PhraseScoreLog(BaseModel):
    """История оценок по одной фразе (до/после)."""

    model_config = ConfigDict(frozen=True)

    phrase_id: str = Field(min_length=1, max_length=128)
    composite_scores: tuple[float, ...] = ()
