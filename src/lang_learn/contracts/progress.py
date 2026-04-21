"""Контракт хранилища прогресса (этап 0 / 6)."""

from abc import ABC, abstractmethod

from lang_learn.schemas.common import EntityId
from lang_learn.schemas.learning import AttemptRecord, LearningProfile


class ProgressRepository(ABC):
    """Абстракция над БД/файлами для профиля и попыток."""

    def close(self) -> None:
        """Освободить ресурсы (соединение с БД и т.п.); по умолчанию — no-op."""
        return None

    @abstractmethod
    def load_profile(self, user_id: EntityId) -> LearningProfile | None:
        """Загрузить профиль пользователя."""

    @abstractmethod
    def save_profile(self, profile: LearningProfile) -> None:
        """Сохранить (создать или обновить) профиль."""

    @abstractmethod
    def save_attempt(self, attempt: AttemptRecord) -> None:
        """Записать попытку для аналитики и SRS."""

    @abstractmethod
    def list_attempts(
        self,
        user_id: EntityId,
        *,
        limit: int = 200,
    ) -> tuple[AttemptRecord, ...]:
        """Последние попытки пользователя (новые первыми)."""

    @abstractmethod
    def enqueue_review(
        self,
        user_id: EntityId,
        *,
        due_utc: str,
        item_kind: str,
        item_ref: str,
        payload: dict[str, object],
    ) -> None:
        """Добавить элемент в очередь повторений (SRS / слабые места)."""
