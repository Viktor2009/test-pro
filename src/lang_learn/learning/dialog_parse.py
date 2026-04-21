"""Разбор JSON ответа модели и безопасный fallback."""

from __future__ import annotations

import json
import re
from typing import Any

from pydantic import ValidationError

from lang_learn.schemas.dialog import StructuredDialogResponse

_JSON_FENCE = re.compile(
    r"^\s*```(?:json)?\s*\n?(.*?)\n?```\s*$",
    re.DOTALL | re.IGNORECASE,
)


def strip_json_fences(raw: str) -> str:
    """Убрать обрамление ```json ... ``` если модель его добавила."""
    text = raw.strip()
    m = _JSON_FENCE.match(text)
    if m:
        return m.group(1).strip()
    return text


def parse_structured_dialog(raw: str) -> tuple[StructuredDialogResponse, bool]:
    """
    Распарсить ``StructuredDialogResponse`` из текста LLM.

    Returns:
        ``(response, fallback_used)``.
    """
    cleaned = strip_json_fences(raw)
    try:
        data: Any = json.loads(cleaned)
        model = StructuredDialogResponse.model_validate(data)
        return model, False
    except (json.JSONDecodeError, ValidationError, TypeError, ValueError):
        return _fallback_response(raw), True


def _fallback_response(raw: str) -> StructuredDialogResponse:
    """Текстовый запасной ответ, если JSON невалиден."""
    reply = raw.strip()
    if not reply:
        reply = "Извините, не удалось разобрать ответ модели."
    reply = reply[:2000]
    return StructuredDialogResponse(
        assistant_reply=reply,
        corrections=(),
        new_vocabulary=(),
        next_action="continue",
    )
