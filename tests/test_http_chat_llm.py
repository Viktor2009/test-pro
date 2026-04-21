"""HTTP LLM: конфигурация из окружения и разбор ответа (без реальной сети)."""

from __future__ import annotations

import io
import json
from unittest.mock import patch

import pytest

from lang_learn.providers.http_chat_llm import HttpChatCompletionsLLMProvider
from lang_learn.schemas.llm import (
    ChatMessage,
    ChatRole,
    LLMProviderConfig,
    LLMRequest,
)


def _sample_openai_response() -> bytes:
    payload = {
        "id": "chatcmpl-test",
        "model": "gpt-4o-mini",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": (
                        '{"assistant_reply":"OK","corrections":[],"'
                        'new_vocabulary":[],"next_action":"continue"}'
                    ),
                },
                "finish_reason": "stop",
            },
        ],
        "usage": {"prompt_tokens": 1, "completion_tokens": 2},
    }
    return json.dumps(payload).encode("utf-8")


@pytest.fixture
def env_ok(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LANG_LEARN_HTTP_LLM_BASE_URL", "https://example.com/v1")
    monkeypatch.setenv("LANG_LEARN_HTTP_LLM_API_KEY", "test-secret-not-real")
    monkeypatch.setenv("LANG_LEARN_HTTP_LLM_MODEL", "gpt-4o-mini")


def test_http_llm_missing_base_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("LANG_LEARN_HTTP_LLM_BASE_URL", raising=False)
    monkeypatch.setenv("LANG_LEARN_HTTP_LLM_API_KEY", "x")
    prov = HttpChatCompletionsLLMProvider()
    req = LLMRequest(
        messages=(ChatMessage(role=ChatRole.USER, content="Hi"),),
        config=LLMProviderConfig(model="stub"),
    )
    with pytest.raises(ValueError, match="LANG_LEARN_HTTP_LLM_BASE_URL"):
        prov.complete(req)


def test_http_llm_missing_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LANG_LEARN_HTTP_LLM_BASE_URL", "https://example.com/v1")
    monkeypatch.delenv("LANG_LEARN_HTTP_LLM_API_KEY", raising=False)
    prov = HttpChatCompletionsLLMProvider()
    req = LLMRequest(
        messages=(ChatMessage(role=ChatRole.USER, content="Hi"),),
        config=LLMProviderConfig(model="stub"),
    )
    with pytest.raises(ValueError, match="LANG_LEARN_HTTP_LLM_API_KEY"):
        prov.complete(req)


def test_http_llm_complete_success(env_ok: None) -> None:
    class _Resp:
        def __enter__(self) -> "_Resp":
            return self

        def __exit__(self, *args: object) -> None:
            return None

        def read(self) -> bytes:
            return _sample_openai_response()

    prov = HttpChatCompletionsLLMProvider()
    req = LLMRequest(
        messages=(ChatMessage(role=ChatRole.USER, content="Hi"),),
        config=LLMProviderConfig(model="stub", response_format_json=True),
    )

    with patch("urllib.request.urlopen", return_value=_Resp()) as op:
        res = prov.complete(req)

    assert "assistant_reply" in res.text
    assert res.finish_reason == "stop"
    assert res.raw is not None
    assert res.raw.get("model") == "gpt-4o-mini"

    op.assert_called_once()
    call_req = op.call_args[0][0]
    assert getattr(call_req, "full_url", "") == "https://example.com/v1/chat/completions"
    sent = json.loads(call_req.data.decode("utf-8"))
    assert sent["model"] == "gpt-4o-mini"
    assert sent["response_format"] == {"type": "json_object"}
    hdrs = {k: v for k, v in call_req.header_items()}
    assert hdrs.get("Authorization") == "Bearer test-secret-not-real"


def test_http_llm_api_error_json(env_ok: None) -> None:
    prov = HttpChatCompletionsLLMProvider()
    req = LLMRequest(
        messages=(ChatMessage(role=ChatRole.USER, content="Hi"),),
        config=LLMProviderConfig(model="stub"),
    )
    err_body = json.dumps({"error": {"message": "invalid"}}).encode()
    import urllib.error

    exc = urllib.error.HTTPError(
        url="https://example.com/v1/chat/completions",
        code=401,
        msg="Unauthorized",
        hdrs=None,
        fp=io.BytesIO(err_body),
    )

    with patch("urllib.request.urlopen", side_effect=exc):
        with pytest.raises(RuntimeError, match="HTTP 401"):
            prov.complete(req)


def test_registry_lists_http_openai() -> None:
    from lang_learn.plugins.bootstrap import create_default_registry

    reg = create_default_registry(with_audio_extras=False)
    names = reg.list_llm()
    assert "http_openai" in names
    assert "stub" in names
