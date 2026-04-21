"""
HTTP-клиент Chat Completions в стиле OpenAI (POST ``/chat/completions``).

Секреты и базовый URL задаются через переменные окружения (не хардкодить в коде).
При старте CLI и GUI подгружается ``.env`` — см. ``lang_learn.config.dotenv_load``.

Переменные окружения
--------------------
``LANG_LEARN_HTTP_LLM_BASE_URL``
    База API без завершающего слэша, например ``https://api.openai.com/v1``.
    Совместимые прокси/альтернативные эндпоинты — тот же путь ``/chat/completions``.

``LANG_LEARN_HTTP_LLM_API_KEY``
    Ключ для заголовка ``Authorization: Bearer …``. Обязателен для реального вызова.

``LANG_LEARN_HTTP_LLM_MODEL`` (необязательно)
    Имя модели на стороне провайдера. По умолчанию: ``gpt-4o-mini``.

``LANG_LEARN_HTTP_LLM_TIMEOUT_SEC`` (необязательно)
    Таймаут HTTP в секундах. По умолчанию: ``60``.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any, Literal, cast

from lang_learn.contracts.llm import LLMProvider
from lang_learn.schemas.llm import ChatMessage, LLMRequest, LLMResult


def _messages_to_openai(messages: tuple[ChatMessage, ...]) -> list[dict[str, str]]:
    return [{"role": m.role.value, "content": m.content} for m in messages]


def _read_error_body(exc: urllib.error.HTTPError) -> str:
    try:
        return exc.read().decode("utf-8", errors="replace")[:4000]
    except OSError:
        return str(exc.reason or exc)


class HttpChatCompletionsLLMProvider(LLMProvider):
    """
    Минимальный шаблон: один POST на ``{base}/chat/completions``.

    Поля ``LLMRequest.config`` (температура, ``max_tokens``, JSON-режим) пробрасываются
    в тело запроса. Имя модели в теле берётся из ``LANG_LEARN_HTTP_LLM_MODEL``, чтобы
    не смешивать его с ключом провайдера в реестре (например ``http_openai``).
    """

    def complete(self, request: LLMRequest) -> LLMResult:
        raw_base = os.environ.get("LANG_LEARN_HTTP_LLM_BASE_URL") or ""
        base = raw_base.strip().rstrip("/")
        if not base:
            msg = (
                "Не задан LANG_LEARN_HTTP_LLM_BASE_URL "
                "(например https://api.openai.com/v1)"
            )
            raise ValueError(msg)

        key = (os.environ.get("LANG_LEARN_HTTP_LLM_API_KEY") or "").strip()
        if not key:
            msg = "Не задан LANG_LEARN_HTTP_LLM_API_KEY (ключ не хранится в коде)."
            raise ValueError(msg)

        model = (os.environ.get("LANG_LEARN_HTTP_LLM_MODEL") or "").strip()
        if not model:
            model = "gpt-4o-mini"

        timeout_raw = (os.environ.get("LANG_LEARN_HTTP_LLM_TIMEOUT_SEC") or "").strip()
        try:
            timeout = float(timeout_raw) if timeout_raw else 60.0
        except ValueError:
            timeout = 60.0

        url = f"{base}/chat/completions"
        payload: dict[str, Any] = {
            "model": model,
            "messages": _messages_to_openai(request.messages),
            "temperature": request.config.temperature,
        }
        if request.config.max_tokens is not None:
            payload["max_tokens"] = request.config.max_tokens
        if request.config.response_format_json:
            payload["response_format"] = {"type": "json_object"}

        body_bytes = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        http_req = urllib.request.Request(
            url,
            data=body_bytes,
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(http_req, timeout=timeout) as resp:
                raw_text = resp.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            detail = _read_error_body(exc)
            msg = f"HTTP {exc.code} при вызове LLM API: {detail}"
            raise RuntimeError(msg) from exc
        except urllib.error.URLError as exc:
            msg = f"Сетевая ошибка LLM API: {exc.reason!s}"
            raise RuntimeError(msg) from exc

        try:
            data: Any = json.loads(raw_text)
        except json.JSONDecodeError as exc:
            msg = f"Ответ API не JSON: {raw_text[:500]!r}"
            raise RuntimeError(msg) from exc

        if isinstance(data, dict) and data.get("error"):
            err = data["error"]
            if isinstance(err, dict):
                emsg = str(err.get("message", err))
            else:
                emsg = str(err)
            raise RuntimeError(f"Ошибка API: {emsg}")

        choices = data.get("choices") if isinstance(data, dict) else None
        if not isinstance(choices, list) or not choices:
            raise RuntimeError(f"В ответе API нет choices: {raw_text[:800]!r}")

        first = choices[0]
        if not isinstance(first, dict):
            raise RuntimeError("Некорректный элемент choices[0]")

        message = first.get("message")
        if not isinstance(message, dict):
            raise RuntimeError("В ответе API нет message")

        content = message.get("content")
        if not isinstance(content, str) or not content.strip():
            raise RuntimeError("В ответе API пустое content")

        finish = first.get("finish_reason")
        fr = cast(
            Literal["stop", "length", "content_filter", "other"],
            finish
            if finish in ("stop", "length", "content_filter")
            else "other",
        )

        slim_raw: dict[str, object] = {
            "id": data.get("id", ""),
            "model": data.get("model", ""),
            "usage": data.get("usage", {}),
        }
        return LLMResult(
            text=content.strip(),
            finish_reason=fr,
            raw=slim_raw,
        )
