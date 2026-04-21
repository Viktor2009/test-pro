"""Загрузка travel-сценариев."""

from lang_learn.learning.travel_loader import load_travel_bundle


def test_travel_bundle_has_six_scenarios() -> None:
    bundle = load_travel_bundle()
    assert len(bundle.scenarios) == 6
    slugs = {s.slug for s in bundle.scenarios}
    assert slugs == {
        "airport",
        "emergency",
        "hotel",
        "pharmacy",
        "restaurant",
        "shop",
    }


def test_airport_has_survival_phrases() -> None:
    bundle = load_travel_bundle()
    airport = next(s for s in bundle.scenarios if s.slug == "airport")
    surv = [p for p in airport.phrases if p.survival]
    assert len(surv) >= 2
