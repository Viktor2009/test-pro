"""Минимальная заглушка STT для сборки и unit-тестов без внешних API."""

from lang_learn.contracts.stt import STTProvider
from lang_learn.schemas.audio import STTRequest, STTResult


class StubSTTProvider(STTProvider):
    """Возвращает фиксированный транскрипт и нулевую уверенность."""

    def transcribe(self, request: STTRequest) -> STTResult:
        """Имитация распознавания без анализа сигнала."""
        _ = request
        return STTResult(text="", confidence=0.0, segments=())
