"""
Расширяемые сценарии голосовой фазы урока алфавита (Pre-A0 GUI).

Для шага «прослушай эталон → пауза → ответ с микрофона» UI выбирает
обработчик по текущему ``ExercisePayload``. Новые режимы (например отдельная
логика для сочетаний ``ch``) подключаются через ``register_alphabet_voice_flow``
без правок основной панели ``pre_a0_lesson``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from lang_learn.schemas.learning import ExercisePayload
from lang_learn.schemas.pre_a0 import ExerciseKind


@dataclass(frozen=True)
class VoicePhaseTiming:
    """Пауза после эталона и длительность записи с микрофона (секунды)."""

    silence_after_reference_s: float = 2.5
    record_duration_s: float = 5.0


@runtime_checkable
class AlphabetVoiceFlow(Protocol):
    """Сценарий: для каких упражнений включать авто-запись и с какими таймингами."""

    def matches(self, ex: ExercisePayload) -> bool:
        """Подходит ли упражнение для голосовой фазы после эталона."""

    def timing(self, ex: ExercisePayload) -> VoicePhaseTiming:
        """Тайминги для данного шага (можно различать по ``ex``)."""


class ListenRepeatLetterVoiceFlow:
    """Первый блок алфавита: LISTEN_REPEAT по одной букве (``letter_id``)."""

    def matches(self, ex: ExercisePayload) -> bool:
        return (
            ex.kind == ExerciseKind.LISTEN_REPEAT.value
            and bool(ex.metadata.get("letter_id"))
        )

    def timing(self, ex: ExercisePayload) -> VoicePhaseTiming:
        _ = ex
        return VoicePhaseTiming()


class ReadAloudLetterVoiceFlow:
    """READ_ALOUD_COMPARE по одной букве: запись запускается сразу (без паузы)."""

    def matches(self, ex: ExercisePayload) -> bool:
        return (
            ex.kind == ExerciseKind.READ_ALOUD_COMPARE.value
            and bool(ex.metadata.get("letter_id"))
        )

    def timing(self, ex: ExercisePayload) -> VoicePhaseTiming:
        _ = ex
        return VoicePhaseTiming(
            silence_after_reference_s=0.0,
            record_duration_s=4.0,
        )


# Сначала проверяются зарегистрированные сценарии (в начале списка), затем встроенные.
_VOICE_FLOWS: list[AlphabetVoiceFlow] = [
    ListenRepeatLetterVoiceFlow(),
    ReadAloudLetterVoiceFlow(),
]


def register_alphabet_voice_flow(flow: AlphabetVoiceFlow) -> None:
    """
    Подключить сценарий голосовой фазы (вызывается до или во время работы GUI).

    Новые сценарии обычно вставляются в начало очереди, чтобы перекрывать
    встроенные при совпадении ``matches``.
    """
    _VOICE_FLOWS.insert(0, flow)


def pick_alphabet_voice_flow(ex: ExercisePayload) -> AlphabetVoiceFlow | None:
    """Первый сценарий, подходящий к упражнению, или ``None`` (только ручной ввод)."""
    for flow in _VOICE_FLOWS:
        if flow.matches(ex):
            return flow
    return None
