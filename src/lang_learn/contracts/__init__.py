"""Абстрактные контракты провайдеров и ядра обучения."""

from lang_learn.contracts.lesson import LessonEngine
from lang_learn.contracts.llm import LLMProvider
from lang_learn.contracts.progress import ProgressRepository
from lang_learn.contracts.stt import STTProvider
from lang_learn.contracts.tts import TTSProvider

__all__ = [
    "LLMProvider",
    "LessonEngine",
    "ProgressRepository",
    "STTProvider",
    "TTSProvider",
]
