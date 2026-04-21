"""Заглушка LLM."""

from lang_learn.providers.stub_llm import StubLLMProvider
from lang_learn.schemas.llm import (
    ChatMessage,
    ChatRole,
    LLMProviderConfig,
    LLMRequest,
)


def test_stub_llm_returns_json_text() -> None:
    p = StubLLMProvider()
    req = LLMRequest(
        messages=(ChatMessage(role=ChatRole.USER, content="hello"),),
        config=LLMProviderConfig(model="stub"),
    )
    out = p.complete(req)
    assert "assistant_reply" in out.text
    assert "new_vocabulary" in out.text
    assert "continue" in out.text
