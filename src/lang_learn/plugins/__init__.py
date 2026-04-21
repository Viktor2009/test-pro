"""Расширяемость: реестр провайдеров (этап 7)."""

from lang_learn.plugins.bootstrap import (
    create_default_lesson_engine_registry,
    create_default_registry,
    register_audio_providers,
    register_builtin_lesson_engines,
    register_builtin_providers,
)
from lang_learn.plugins.lesson_registry import LessonEngineRegistry
from lang_learn.plugins.registry import ProviderKind, ProviderRegistry

__all__ = [
    "LessonEngineRegistry",
    "ProviderKind",
    "ProviderRegistry",
    "create_default_lesson_engine_registry",
    "create_default_registry",
    "register_audio_providers",
    "register_builtin_lesson_engines",
    "register_builtin_providers",
]
