"""Сервис travel-сессий."""

import pytest

from lang_learn.learning.travel_session import TravelScenarioService


def test_build_context_stress_vs_calm() -> None:
    svc = TravelScenarioService.load_default()
    calm = svc.build_dialog_context(
        "airport",
        "Where is my gate?",
        variation_level=2,
        stress=False,
    )
    stress = svc.build_dialog_context(
        "airport",
        "Where is my gate?",
        variation_level=2,
        stress=True,
    )
    assert "Режим стресса" in stress.session_goal
    assert "Режим стресса" not in calm.session_goal
    assert stress.max_reply_sentences == 2


def test_unknown_slug_raises() -> None:
    svc = TravelScenarioService.load_default()
    with pytest.raises(KeyError):
        svc.get_scenario("no-such-scenario")
