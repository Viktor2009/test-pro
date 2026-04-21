"""DialogOrchestrator с StubLLM и опционально StubTTS."""

from lang_learn.contracts.llm import LLMProvider
from lang_learn.learning.dialog_orchestrator import DialogOrchestrator
from lang_learn.providers.stub_llm import StubLLMProvider
from lang_learn.providers.stub_tts import StubTTSProvider
from lang_learn.schemas.dialog import DialogSessionContext
from lang_learn.schemas.llm import LLMProviderConfig, LLMRequest, LLMResult


class _BadJsonLLM(LLMProvider):
    def complete(self, request: LLMRequest) -> LLMResult:
        _ = request
        return LLMResult(text="<<<not-json>>>", finish_reason="stop")


def test_orchestrator_valid_stub() -> None:
    ctx = DialogSessionContext(
        topic="Shop",
        session_goal="Buy water.",
        target_language="en-US",
        user_latest_message="How much is it?",
    )
    out = DialogOrchestrator(StubLLMProvider()).run_turn(
        ctx,
        LLMProviderConfig(model="stub"),
    )
    assert out.fallback_used is False
    assert out.structured.assistant_reply == "stub"
    assert out.tts_audio is None


def test_orchestrator_fallback() -> None:
    ctx = DialogSessionContext(
        topic="Shop",
        session_goal="Buy water.",
        target_language="en-US",
        user_latest_message="How much is it?",
    )
    out = DialogOrchestrator(_BadJsonLLM()).run_turn(
        ctx,
        LLMProviderConfig(model="x"),
    )
    assert out.fallback_used is True
    assert "<<<not-json>>>" in out.structured.assistant_reply


def test_orchestrator_with_stub_tts() -> None:
    ctx = DialogSessionContext(
        topic="Shop",
        session_goal="Buy water.",
        target_language="en-US",
        user_latest_message="How much is it?",
    )
    out = DialogOrchestrator(StubLLMProvider(), tts=StubTTSProvider()).run_turn(
        ctx,
        LLMProviderConfig(model="stub"),
    )
    assert out.tts_audio is not None
    assert out.tts_format is not None
