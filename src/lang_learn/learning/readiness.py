"""Готовность к поездке по travel-сценариям (этап 6)."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence

from lang_learn.schemas.learning import AttemptRecord
from lang_learn.schemas.progress_analytics import TravelReadinessView

TRAVEL_SLUGS: tuple[str, ...] = (
    "airport",
    "hotel",
    "restaurant",
    "shop",
    "pharmacy",
    "emergency",
)


def _mean(values: Sequence[float]) -> float:
    if not values:
        return 0.0
    return float(sum(values) / len(values))


def travel_readiness_view(attempts: Sequence[AttemptRecord]) -> TravelReadinessView:
    buckets: dict[str, list[float]] = defaultdict(list)
    for att in attempts:
        slug = (att.details or {}).get("scenario_slug")
        if not isinstance(slug, str) or att.score is None:
            continue
        buckets[slug].append(float(att.score))
    by_scenario = {slug: _mean(buckets[slug]) for slug in TRAVEL_SLUGS}
    vals = [by_scenario[s] for s in TRAVEL_SLUGS]
    percent = 100.0 * sum(vals) / float(len(TRAVEL_SLUGS))
    return TravelReadinessView(percent=percent, by_scenario=by_scenario)
