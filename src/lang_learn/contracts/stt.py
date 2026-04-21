"""Контракт STT: аудио -> текст (+ confidence)."""

from abc import ABC, abstractmethod

from lang_learn.schemas.audio import STTRequest, STTResult


class STTProvider(ABC):
    """Провайдер распознавания речи (заменяемая реализация)."""

    @abstractmethod
    def transcribe(self, request: STTRequest) -> STTResult:
        """Распознать речь по переданному аудио."""
