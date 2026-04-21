"""Контракт TTS: текст -> аудио."""

from abc import ABC, abstractmethod

from lang_learn.schemas.audio import TTSRequest, TTSResult


class TTSProvider(ABC):
    """Провайдер синтеза речи (заменяемая реализация)."""

    @abstractmethod
    def synthesize(self, request: TTSRequest) -> TTSResult:
        """Синтезировать речь из текста."""
