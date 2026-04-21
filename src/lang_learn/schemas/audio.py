"""Схемы для TTS/STT (этап 1 — аудио-ядро)."""

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from lang_learn.schemas.common import LanguageCode


class AudioFormat(str, Enum):
    """Формат сырого аудио на границе провайдера."""

    WAV = "wav"
    PCM = "pcm"
    MP3 = "mp3"
    OGG_OPUS = "ogg_opus"


class TTSRequest(BaseModel):
    """Запрос синтеза речи."""

    model_config = ConfigDict(frozen=True)

    text: str = Field(min_length=1)
    language: LanguageCode
    voice_id: str | None = None
    speed: float = Field(default=1.0, ge=0.25, le=4.0)
    audio_format: AudioFormat = AudioFormat.WAV
    sample_rate_hz: int | None = Field(default=None, ge=8000, le=48000)


class TTSResult(BaseModel):
    """Ответ TTS: сырое аудио и метаданные."""

    model_config = ConfigDict(frozen=True)

    audio: bytes
    format: AudioFormat
    sample_rate_hz: int | None = None
    duration_ms: int | None = Field(default=None, ge=0)


class STTSegment(BaseModel):
    """Фрагмент распознанного текста (для будущих сегментированных STT)."""

    model_config = ConfigDict(frozen=True)

    text: str
    start_ms: int | None = Field(default=None, ge=0)
    end_ms: int | None = Field(default=None, ge=0)
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)


class STTRequest(BaseModel):
    """Запрос распознавания речи."""

    model_config = ConfigDict(frozen=True)

    audio: bytes = Field(min_length=1)
    language: LanguageCode | None = None
    audio_format: AudioFormat = AudioFormat.WAV
    sample_rate_hz: int | None = Field(default=None, ge=8000, le=48000)
    vad_filter: bool | None = Field(
        default=None,
        description="None — поведение провайдера по умолчанию (у Whisper: True).",
    )
    initial_prompt: str | None = Field(
        default=None,
        max_length=448,
        description="Подсказка для модели (например ожидаемые слова).",
    )


class STTResult(BaseModel):
    """Результат STT: полный текст, уверенность, опционально сегменты."""

    model_config = ConfigDict(frozen=True)

    text: str
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    segments: tuple[STTSegment, ...] = ()
