"""Конфигурируемые учебные траектории (этап 7)."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class TrajectorySpec(BaseModel):
    """Одна траектория: набор сценариев и ссылок на учебные модули."""

    model_config = ConfigDict(frozen=True)

    id: str = Field(min_length=1, max_length=64, pattern=r"^[a-z][a-z0-9_]*$")
    title: str = Field(min_length=1, max_length=256)
    description: str = Field(default="", max_length=2000)
    scenario_slugs: tuple[str, ...] = ()
    module_refs: tuple[str, ...] = Field(
        default=(),
        description="Логические модули: pre_a0, travel, dialog, pronunciation, …",
    )


class TrajectoryBundle(BaseModel):
    """Набор траекторий из JSON (пакетный или пользовательский файл)."""

    model_config = ConfigDict(frozen=True)

    version: int = Field(default=1, ge=1)
    items: tuple[TrajectorySpec, ...] = Field(min_length=1)
