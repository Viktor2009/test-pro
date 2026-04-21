"""Сводка прогресса: компетенции, KPI, travel (этап 6)."""

from __future__ import annotations

from collections.abc import Sequence

from lang_learn.learning.competency import competency_from_attempts
from lang_learn.learning.kpi_engine import compute_learning_kpis
from lang_learn.learning.readiness import travel_readiness_view
from lang_learn.schemas.learning import AttemptRecord
from lang_learn.schemas.progress_analytics import ProgressOverview


def compute_progress_overview(attempts: Sequence[AttemptRecord]) -> ProgressOverview:
    """Единая точка входа для дашборда и CLI."""
    return ProgressOverview(
        competency=competency_from_attempts(attempts),
        kpis=compute_learning_kpis(attempts),
        travel=travel_readiness_view(attempts),
    )
