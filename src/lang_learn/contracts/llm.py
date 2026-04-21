"""Контракт LLM: запрос -> ответ (сырой текст / JSON на стороне оркестратора)."""

from abc import ABC, abstractmethod

from lang_learn.schemas.llm import LLMRequest, LLMResult


class LLMProvider(ABC):
    """Провайдер языковой модели (заменяемая реализация)."""

    @abstractmethod
    def complete(self, request: LLMRequest) -> LLMResult:
        """Выполнить запрос к модели и вернуть результат."""
