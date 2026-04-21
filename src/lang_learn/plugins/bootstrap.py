"""Регистрация встроенных провайдеров в реестре (этап 7)."""

from __future__ import annotations

from lang_learn.contracts.lesson import LessonEngine
from lang_learn.contracts.llm import LLMProvider
from lang_learn.contracts.stt import STTProvider
from lang_learn.contracts.tts import TTSProvider
from lang_learn.plugins.lesson_registry import LessonEngineRegistry
from lang_learn.plugins.registry import ProviderRegistry
from lang_learn.providers.stub_llm import StubLLMProvider
from lang_learn.providers.stub_stt import StubSTTProvider
from lang_learn.providers.stub_tts import StubTTSProvider


def _pre_a0_engine_factory() -> LessonEngine:
    from lang_learn.learning.course_loader import load_packaged_en_sample
    from lang_learn.learning.pre_a0_engine import PreA0LessonEngine

    return PreA0LessonEngine(load_packaged_en_sample())


def register_builtin_lesson_engines(registry: LessonEngineRegistry) -> None:
    """Зарегистрировать встроенные движки уроков."""
    registry.register("pre_a0", _pre_a0_engine_factory)


def _http_chat_llm_factory() -> LLMProvider:
    from lang_learn.providers.http_chat_llm import HttpChatCompletionsLLMProvider

    return HttpChatCompletionsLLMProvider()


def register_builtin_providers(registry: ProviderRegistry) -> None:
    """Зарегистрировать ``stub`` для LLM/STT/TTS (всегда доступно)."""
    registry.register_llm("stub", StubLLMProvider)
    registry.register_llm("http_openai", _http_chat_llm_factory)
    registry.register_stt("stub", StubSTTProvider)
    registry.register_tts("stub", StubTTSProvider)


def _pyttsx3_tts_factory() -> TTSProvider:
    from lang_learn.providers.pyttsx3_tts import Pyttsx3TTSProvider

    return Pyttsx3TTSProvider()


def _faster_whisper_stt_factory() -> STTProvider:
    from lang_learn.providers.faster_whisper_stt import FasterWhisperSTTProvider

    return FasterWhisperSTTProvider()


def register_audio_providers(registry: ProviderRegistry) -> None:
    """
    Опционально зарегистрировать локальные аудио-провайдеры (тяжёлые зависимости).

    Вызывать только если установлен extra ``[audio]``; иначе возможен ImportError.
    """
    registry.register_tts("pyttsx3", _pyttsx3_tts_factory)
    registry.register_stt("faster_whisper", _faster_whisper_stt_factory)


def create_default_registry(*, with_audio_extras: bool = False) -> ProviderRegistry:
    """
    Новый реестр с встроенными stub.

    При ``with_audio_extras`` добавляются pyttsx3 и faster_whisper.
    """
    reg = ProviderRegistry()
    register_builtin_providers(reg)
    if with_audio_extras:
        register_audio_providers(reg)
    return reg


def create_default_lesson_engine_registry() -> LessonEngineRegistry:
    """Реестр с ``pre_a0`` и дальнейшими встроенными движками."""
    reg = LessonEngineRegistry()
    register_builtin_lesson_engines(reg)
    return reg
