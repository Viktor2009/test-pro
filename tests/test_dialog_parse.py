"""Парсинг JSON ответа диалога и fallback."""

import json

from lang_learn.learning.dialog_parse import parse_structured_dialog, strip_json_fences
from lang_learn.schemas.dialog import StructuredDialogResponse


def test_parse_valid_json() -> None:
    raw = json.dumps(
        {
            "assistant_reply": "Gate B12 is on your left.",
            "corrections": [],
            "new_vocabulary": [{"term": "gate", "gloss": "выход"}],
            "next_action": "continue",
        },
    )
    model, fb = parse_structured_dialog(raw)
    assert fb is False
    assert model.assistant_reply.startswith("Gate")
    assert len(model.new_vocabulary) == 1


def test_parse_json_in_fence() -> None:
    inner = (
        '{"assistant_reply":"hi","corrections":[],"new_vocabulary":[],'
        '"next_action":"summarize"}'
    )
    raw = f"```json\n{inner}\n```"
    assert strip_json_fences(raw) == inner
    model, fb = parse_structured_dialog(raw)
    assert fb is False
    assert model.next_action == "summarize"


def test_parse_fallback_on_garbage() -> None:
    model, fb = parse_structured_dialog("not json at all")
    assert fb is True
    assert isinstance(model, StructuredDialogResponse)
    assert model.assistant_reply == "not json at all"
    assert model.next_action == "continue"
