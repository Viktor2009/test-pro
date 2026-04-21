"""Агрегаты прогресса, KPI и готовность к поездке (этап 6)."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class CompetencySnapshot(BaseModel):
    """Профиль компетенций в диапазоне ``[0, 1]`` по осям."""

    model_config = ConfigDict(frozen=True)

    lexicon: float = Field(ge=0.0, le=1.0)
    comprehension: float = Field(ge=0.0, le=1.0)
    pronunciation: float = Field(ge=0.0, le=1.0)
    dialog_scenario: float = Field(ge=0.0, le=1.0)


class LearningKPIs(BaseModel):
    """Ключевые показатели обучения (нормализовано ``[0, 1]``)."""

    model_config = ConfigDict(frozen=True)

    completion_rate: float = Field(ge=0.0, le=1.0)
    retention_rate: float = Field(ge=0.0, le=1.0)
    pronunciation_score: float = Field(ge=0.0, le=1.0)
    scenario_readiness: float = Field(ge=0.0, le=1.0)


class TravelReadinessView(BaseModel):
    """Готовность к поездке по travel-сценариям."""

    model_config = ConfigDict(frozen=True)

    percent: float = Field(ge=0.0, le=100.0)
    by_scenario: dict[str, float] = Field(
        default_factory=dict,
        description="Средняя оценка (0–1) по slug сценария.",
    )


class ProgressOverview(BaseModel):
    """Сводка для дашборда: компетенции + KPI + travel."""

    model_config = ConfigDict(frozen=True)

    competency: CompetencySnapshot
    kpis: LearningKPIs
    travel: TravelReadinessView
