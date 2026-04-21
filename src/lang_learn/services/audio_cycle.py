"""
Каркас аудио-цикла этапа 1: текст -> TTS; запись -> STT.

Захват с микрофона и UI — вне этого модуля.
"""

from lang_learn.audio_io.recorder import MicrophoneRecorder
from lang_learn.contracts.stt import STTProvider
from lang_learn.contracts.tts import TTSProvider
from lang_learn.schemas.audio import STTRequest, STTResult, TTSRequest, TTSResult
from lang_learn.schemas.common import LanguageCode


class AudioCycleService:
    """
    Оркестрация базового цикла озвучивания и распознавания.

    Захват с микрофона и воспроизведение — вне этого класса (Audio I/O Layer).
    """

    def __init__(self, tts: TTSProvider, stt: STTProvider) -> None:
        self._tts = tts
        self._stt = stt

    def speak_text(
        self,
        text: str,
        language: LanguageCode,
        *,
        voice_id: str | None = None,
        speed: float = 1.0,
    ) -> TTSResult:
        """Синтез речи для переданного текста (этап 1)."""
        req = TTSRequest(
            text=text,
            language=language,
            voice_id=voice_id,
            speed=speed,
        )
        return self._tts.synthesize(req)

    def transcribe_audio(
        self,
        audio: bytes,
        *,
        language: LanguageCode | None = None,
    ) -> STTResult:
        """Распознавание переданного аудио-буфера (этап 1)."""
        req = STTRequest(audio=audio, language=language)
        return self._stt.transcribe(req)

    def record_and_transcribe(
        self,
        recorder: MicrophoneRecorder,
        duration_s: float,
        *,
        language: LanguageCode | None = None,
    ) -> STTResult:
        """Запись с микрофона и распознавание (этап 1)."""
        wav = recorder.record_seconds(duration_s)
        return self.transcribe_audio(wav, language=language)
