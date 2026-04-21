"""Минимальная заглушка TTS для сборки и unit-тестов без внешних API."""

from lang_learn.contracts.tts import TTSProvider
from lang_learn.schemas.audio import AudioFormat, TTSRequest, TTSResult


class StubTTSProvider(TTSProvider):
    """Возвращает пустой байтовый буфер фиксированного «формата»."""

    def synthesize(self, request: TTSRequest) -> TTSResult:
        """Имитация синтеза: метаданные сохраняются, аудио пустое."""
        return TTSResult(
            audio=b"",
            format=AudioFormat.WAV,
            sample_rate_hz=request.sample_rate_hz,
            duration_ms=0,
        )
