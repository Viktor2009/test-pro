"""Загрузка travel-сценариев из JSON."""

from __future__ import annotations

import json
from importlib import resources

from lang_learn.schemas.travel import TravelScenarioBundle


def load_travel_bundle_bytes(data: bytes) -> TravelScenarioBundle:
    """Разобрать JSON набора сценариев."""
    raw = json.loads(data.decode("utf-8"))
    return TravelScenarioBundle.model_validate(raw)


def load_travel_bundle() -> TravelScenarioBundle:
    """Загрузить встроенный ``scenarios_bundle.json``."""
    from lang_learn.data import travel as travel_data

    path = resources.files(travel_data).joinpath("scenarios_bundle.json")
    return load_travel_bundle_bytes(path.read_bytes())
