"""KPI по истории попыток (этап 6)."""

from __future__ import annotations

from collections.abc import Sequence

from lang_learn.schemas.learning import AttemptRecord
from lang_learn.schemas.progress_analytics import LearningKPIs


def _mean(values: Sequence[float]) -> float:
    if not values:
        return 0.0
    return float(sum(values) / len(values))


def completion_rate(completed: int, total: int) -> float:
    if total <= 0:
        return 0.0
    return min(1.0, float(completed) / float(total))


def retention_rate_recent(scores: Sequence[float]) -> float:
    """Сравнение «ранних» и «поздних» оценок (грубый proxy удержания)."""
    seq = [float(s) for s in scores]
    n = len(seq)
    if n < 2:
        return 0.5
    third = max(1, n // 3)
    early = _mean(seq[:third])
    late = _mean(seq[-third:])
    if early <= 1e-6:
        return 0.5
    return min(1.0, late / early)


def scenario_readiness_score(attempts: Sequence[AttemptRecord]) -> float:
    scores = [
        float(a.score)
        for a in attempts
        if a.score is not None
        and isinstance((a.details or {}).get("scenario_slug"), str)
    ]
    return _mean(scores)


def compute_learning_kpis(
    attempts: Sequence[AttemptRecord],
    *,
    assignments_total: int = 20,
) -> LearningKPIs:
    scored = [a for a in attempts if a.score is not None]
    scores = [float(a.score) for a in scored if a.score is not None]
    pronunciation_score = _mean(scores)
    completed = sum(1 for a in scored if float(a.score or 0.0) >= 0.55)
    comp_rate = completion_rate(
        min(completed, assignments_total),
        max(assignments_total, 1),
    )
    retention = retention_rate_recent(scores)
    scenario = scenario_readiness_score(attempts)
    return LearningKPIs(
        completion_rate=comp_rate,
        retention_rate=retention,
        pronunciation_score=pronunciation_score,
        scenario_readiness=scenario,
    )
