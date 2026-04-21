"""Реестр фабрик STT/TTS/LLM по строковому ключу (plugin-like, этап 7)."""

from __future__ import annotations

from collections.abc import Callable
from enum import Enum

from lang_learn.contracts.llm import LLMProvider
from lang_learn.contracts.stt import STTProvider
from lang_learn.contracts.tts import TTSProvider


class ProviderKind(str, Enum):
    """Тип провайдера для регистрации и разрешения."""

    LLM = "llm"
    STT = "stt"
    TTS = "tts"


class ProviderRegistry:
    """
    Регистрация фабрик ``() -> Provider`` по имени.

    Имена — короткие идентификаторы (``stub``, ``pyttsx3``, …) для CLI и
    внешнего API.
    """

    def __init__(self) -> None:
        self._llm: dict[str, Callable[[], LLMProvider]] = {}
        self._stt: dict[str, Callable[[], STTProvider]] = {}
        self._tts: dict[str, Callable[[], TTSProvider]] = {}

    def register_llm(self, name: str, factory: Callable[[], LLMProvider]) -> None:
        key = name.strip().lower()
        if not key:
            msg = "Имя провайдера LLM не может быть пустым"
            raise ValueError(msg)
        self._llm[key] = factory

    def register_stt(self, name: str, factory: Callable[[], STTProvider]) -> None:
        key = name.strip().lower()
        if not key:
            msg = "Имя провайдера STT не может быть пустым"
            raise ValueError(msg)
        self._stt[key] = factory

    def register_tts(self, name: str, factory: Callable[[], TTSProvider]) -> None:
        key = name.strip().lower()
        if not key:
            msg = "Имя провайдера TTS не может быть пустым"
            raise ValueError(msg)
        self._tts[key] = factory

    def create_llm(self, name: str) -> LLMProvider:
        key = name.strip().lower()
        if key not in self._llm:
            msg = f"Неизвестный LLM-провайдер: {name!r}"
            raise KeyError(msg)
        return self._llm[key]()

    def create_stt(self, name: str) -> STTProvider:
        key = name.strip().lower()
        if key not in self._stt:
            msg = f"Неизвестный STT-провайдер: {name!r}"
            raise KeyError(msg)
        return self._stt[key]()

    def create_tts(self, name: str) -> TTSProvider:
        key = name.strip().lower()
        if key not in self._tts:
            msg = f"Неизвестный TTS-провайдер: {name!r}"
            raise KeyError(msg)
        return self._tts[key]()

    def list_llm(self) -> tuple[str, ...]:
        return tuple(sorted(self._llm))

    def list_stt(self) -> tuple[str, ...]:
        return tuple(sorted(self._stt))

    def list_tts(self) -> tuple[str, ...]:
        return tuple(sorted(self._tts))
