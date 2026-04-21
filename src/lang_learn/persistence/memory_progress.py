"""In-memory реализация ``ProgressRepository``."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence

from lang_learn.contracts.progress import ProgressRepository
from lang_learn.schemas.common import EntityId
from lang_learn.schemas.learning import AttemptRecord, LearningProfile


class MemoryProgressRepository(ProgressRepository):
    """Хранит профиль и попытки в процессе (без SQLite)."""

    def __init__(self) -> None:
        self._profiles: dict[str, LearningProfile] = {}
        self._attempts: dict[str, list[AttemptRecord]] = defaultdict(list)
        self._reviews: dict[str, list[dict[str, object]]] = defaultdict(list)

    def load_profile(self, user_id: EntityId) -> LearningProfile | None:
        return self._profiles.get(user_id)

    def save_profile(self, profile: LearningProfile) -> None:
        self._profiles[profile.user_id] = profile

    def save_attempt(self, attempt: AttemptRecord) -> None:
        self._attempts[attempt.user_id].append(attempt)

    def list_attempts(
        self,
        user_id: EntityId,
        *,
        limit: int = 200,
    ) -> tuple[AttemptRecord, ...]:
        seq = self._attempts.get(user_id, [])
        if limit <= 0:
            return ()
        tail = seq[-limit:]
        return tuple(reversed(tail))

    def enqueue_review(
        self,
        user_id: EntityId,
        *,
        due_utc: str,
        item_kind: str,
        item_ref: str,
        payload: dict[str, object],
    ) -> None:
        self._reviews[user_id].append(
            {
                "due_utc": due_utc,
                "item_kind": item_kind,
                "item_ref": item_ref,
                "payload": payload,
            },
        )

    def list_enqueued_reviews(self, user_id: EntityId) -> Sequence[dict[str, object]]:
        """Только для тестов и отладки."""
        return tuple(self._reviews.get(user_id, ()))
