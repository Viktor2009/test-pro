"""Область пользователя для многопользовательского режима и внешних API (этап 7)."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from lang_learn.schemas.common import EntityId


class UserScope(BaseModel):
    """
    Идентификация обучаемого во внешнем слое (REST, desktop host).

    ``tenant_id`` зарезервирован под изоляцию данных организации/класса.
    """

    model_config = ConfigDict(frozen=True)

    external_user_id: EntityId
    tenant_id: str | None = Field(
        default=None,
        max_length=64,
        description="Необязательный идентификатор арендатора (multi-tenant).",
    )
