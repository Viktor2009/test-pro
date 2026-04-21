"""Реестр учебных движков (LessonEngine) по имени (этап 7)."""

from __future__ import annotations

from collections.abc import Callable

from lang_learn.contracts.lesson import LessonEngine


class LessonEngineRegistry:
    """Фабрики ``() -> LessonEngine`` для расширения типов уроков."""

    def __init__(self) -> None:
        self._factories: dict[str, Callable[[], LessonEngine]] = {}

    def register(self, name: str, factory: Callable[[], LessonEngine]) -> None:
        key = name.strip().lower()
        if not key:
            msg = "Имя движка не может быть пустым"
            raise ValueError(msg)
        self._factories[key] = factory

    def create(self, name: str) -> LessonEngine:
        key = name.strip().lower()
        if key not in self._factories:
            msg = f"Неизвестный LessonEngine: {name!r}"
            raise KeyError(msg)
        return self._factories[key]()

    def list_names(self) -> tuple[str, ...]:
        return tuple(sorted(self._factories))
