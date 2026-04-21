"""Заглушка LLM для сборки и тестов без внешних API."""

from lang_learn.contracts.llm import LLMProvider
from lang_learn.schemas.llm import LLMRequest, LLMResult


class StubLLMProvider(LLMProvider):
    """Возвращает фиксированный JSON-совместимый ответ."""

    def complete(self, request: LLMRequest) -> LLMResult:
        """Имитация ответа модели (структура диалога — в этапе 3)."""
        _ = request
        payload = (
            '{"assistant_reply":"stub","corrections":[],"new_vocabulary":[],'
            '"next_action":"continue"}'
        )
        return LLMResult(text=payload, finish_reason="stop", raw=None)
