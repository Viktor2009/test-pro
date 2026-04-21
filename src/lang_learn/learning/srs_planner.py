"""Простой план повторений по слабым осям (SRS-лайт, этап 6)."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime, timedelta, timezone

from lang_learn.schemas.progress_analytics import CompetencySnapshot


def weak_skill_axes(
    snapshot: CompetencySnapshot,
    *,
    threshold: float = 0.55,
) -> list[str]:
    """Возвращает имена осей со средней оценкой ниже порога."""
    pairs = (
        ("lexicon", snapshot.lexicon),
        ("comprehension", snapshot.comprehension),
        ("pronunciation", snapshot.pronunciation),
        ("dialog_scenario", snapshot.dialog_scenario),
    )
    return [name for name, val in pairs if val < threshold]


def plan_review_items(
    weak_axes: Sequence[str],
    *,
    base_hours: int = 24,
    now: datetime | None = None,
) -> list[tuple[str, str, str]]:
    """
    Кортежи ``(item_kind, item_ref, due_utc_iso)`` для очереди повторений.

    ``item_kind`` = ``skill_axis``, ``item_ref`` = имя оси.
    """
    start = now or datetime.now(timezone.utc)
    out: list[tuple[str, str, str]] = []
    for i, axis in enumerate(weak_axes):
        due = start + timedelta(hours=base_hours * (i + 1))
        due_s = due.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        out.append(("skill_axis", axis, due_s))
    return out
