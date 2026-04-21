"""Этап 7: флаги, реестры, траектории, интеграционные DTO."""

from __future__ import annotations

import json

import pytest

from lang_learn.config.feature_flags import KNOWN_FEATURE_FLAGS, load_feature_flags
from lang_learn.learning.dialog_orchestrator import DialogOrchestrator
from lang_learn.learning.trajectory_service import TrajectoryService
from lang_learn.learning.travel_session import TravelScenarioService
from lang_learn.plugins.bootstrap import (
    create_default_lesson_engine_registry,
    create_default_registry,
)
from lang_learn.plugins.registry import ProviderRegistry
from lang_learn.providers.stub_llm import StubLLMProvider
from lang_learn.schemas.integration_api import (
    HttpDialogTurnRequest,
    HttpDialogTurnResponse,
)
from lang_learn.schemas.learning import LessonContext
from lang_learn.schemas.llm import LLMProviderConfig
from lang_learn.schemas.user_scope import UserScope


def test_load_feature_flags_from_mapping() -> None:
    env = {
        f"LANG_LEARN_FF_{n.upper()}": "1" for n in ("shadowing_beta", "exam_prep_mode")
    }
    flags = load_feature_flags(env)
    assert flags.is_enabled("shadowing_beta")
    assert flags.is_enabled("exam_prep_mode")
    assert not flags.is_enabled("strict_dialog_json")
    assert "unknown" not in KNOWN_FEATURE_FLAGS


def test_load_feature_flags_ignores_unknown() -> None:
    env = {"LANG_LEARN_FF_UNKNOWN_THING": "1"}
    flags = load_feature_flags(env)
    assert flags.enabled_names == frozenset()


def test_provider_registry_create_llm() -> None:
    reg = create_default_registry(with_audio_extras=False)
    llm = reg.create_llm("stub")
    assert isinstance(llm, StubLLMProvider)


def test_provider_registry_unknown() -> None:
    reg = ProviderRegistry()
    with pytest.raises(KeyError):
        reg.create_llm("missing")


def test_trajectory_service_against_travel() -> None:
    ts = TrajectoryService.load_default()
    travel = TravelScenarioService.load_default()
    known = frozenset(s.slug for s in travel.list_scenarios())
    tr = ts.get("travel")
    assert ts.unknown_scenario_slugs(tr, known) == ()


def test_lesson_engine_registry_pre_a0() -> None:
    reg = create_default_lesson_engine_registry()
    eng = reg.create("pre_a0")
    ex = eng.next_exercise(LessonContext(user_id="t"))
    assert ex.exercise_id


def test_http_dialog_roundtrip() -> None:
    req = HttpDialogTurnRequest(
        topic="Shop",
        session_goal="Buy water.",
        level_hint="A1",
        target_language="en-US",
        user_latest_message="How much is this?",
        llm_provider="stub",
    )
    ctx = req.to_session_context()
    assert ctx.topic == "Shop"
    orch = DialogOrchestrator(StubLLMProvider())
    res = orch.run_turn(ctx, LLMProviderConfig(model="stub"))
    out = HttpDialogTurnResponse.from_turn_result(res)
    data = json.loads(out.model_dump_json())
    assert data["structured"]["assistant_reply"] == "stub"
    assert data["fallback_used"] is False


def test_user_scope_model() -> None:
    s = UserScope(external_user_id="u-1", tenant_id="school-9")
    assert s.external_user_id == "u-1"
    assert s.tenant_id == "school-9"
