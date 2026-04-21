"""Снимок компетенций по осям (этап 6)."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence

from lang_learn.schemas.learning import AttemptRecord
from lang_learn.schemas.progress_analytics import CompetencySnapshot

_AXIS_KEYS = (
    "lexicon",
    "comprehension",
    "pronunciation",
    "dialog_scenario",
)


def _mean(values: Sequence[float]) -> float:
    if not values:
        return 0.0
    return float(sum(values) / len(values))


def competency_from_attempts(
    attempts: Sequence[AttemptRecord],
) -> CompetencySnapshot:
    """
    Агрегирует ``score`` по полю ``details['skill_axis']``.

    Если ось не указана, попытка относится к ``pronunciation``.
    """
    buckets: dict[str, list[float]] = defaultdict(list)
    for att in attempts:
        if att.score is None:
            continue
        raw_axis = (att.details or {}).get("skill_axis", "pronunciation")
        axis = str(raw_axis) if raw_axis is not None else "pronunciation"
        if axis not in _AXIS_KEYS:
            axis = "pronunciation"
        buckets[axis].append(float(att.score))
    return CompetencySnapshot(
        lexicon=_mean(buckets["lexicon"]),
        comprehension=_mean(buckets["comprehension"]),
        pronunciation=_mean(buckets["pronunciation"]),
        dialog_scenario=_mean(buckets["dialog_scenario"]),
    )
