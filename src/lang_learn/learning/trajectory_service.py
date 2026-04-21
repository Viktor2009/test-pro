"""Загрузка и выборка учебных траекторий (этап 7)."""

from __future__ import annotations

import json
from importlib import resources

from lang_learn.schemas.trajectory import TrajectoryBundle, TrajectorySpec


def load_trajectory_bundle_bytes(data: bytes) -> TrajectoryBundle:
    """Разобрать JSON набора траекторий."""
    raw = json.loads(data.decode("utf-8"))
    return TrajectoryBundle.model_validate(raw)


def load_default_trajectory_bundle() -> TrajectoryBundle:
    """Встроенный ``data/trajectories/bundle.json``."""
    from lang_learn.data import trajectories as traj_data

    path = resources.files(traj_data).joinpath("bundle.json")
    return load_trajectory_bundle_bytes(path.read_bytes())


class TrajectoryService:
    """Доступ к траекториям по id и проверка slug против travel-набора."""

    def __init__(self, bundle: TrajectoryBundle) -> None:
        self._bundle = bundle
        self._by_id = {item.id: item for item in bundle.items}

    @classmethod
    def load_default(cls) -> TrajectoryService:
        return cls(load_default_trajectory_bundle())

    def list_specs(self) -> tuple[TrajectorySpec, ...]:
        return self._bundle.items

    def get(self, trajectory_id: str) -> TrajectorySpec:
        tid = trajectory_id.strip().lower()
        if tid not in self._by_id:
            msg = f"Unknown trajectory id: {trajectory_id!r}"
            raise KeyError(msg)
        return self._by_id[tid]

    def unknown_scenario_slugs(
        self,
        spec: TrajectorySpec,
        known_slugs: frozenset[str],
    ) -> tuple[str, ...]:
        """Slug-и из спецификации, которых нет в переданном множестве."""
        return tuple(s for s in spec.scenario_slugs if s not in known_slugs)
