"""Контракт учебного движка (этап 0+)."""

from abc import ABC, abstractmethod

from lang_learn.schemas.learning import (
    AttemptFeedback,
    AttemptRecord,
    ExercisePayload,
    LessonContext,
)


class LessonEngine(ABC):
    """Генерация упражнений и оценка ответов (педагогическое ядро)."""

    @abstractmethod
    def next_exercise(self, ctx: LessonContext) -> ExercisePayload:
        """Выдать следующее упражнение в текущем контексте."""

    @abstractmethod
    def submit_attempt(self, attempt: AttemptRecord) -> AttemptFeedback:
        """Принять попытку и вернуть фидбек."""
