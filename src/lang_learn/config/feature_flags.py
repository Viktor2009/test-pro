"""Флаги возможностей из окружения (этап 7)."""

from __future__ import annotations

from collections.abc import Mapping

# Известные флаги (документированный набор; неизвестные ключи игнорируются).
KNOWN_FEATURE_FLAGS: frozenset[str] = frozenset(
    {
        "shadowing_beta",
        "business_scenarios_pack",
        "exam_prep_mode",
        "external_rest_bridge",
        "strict_dialog_json",
    },
)

_ENV_PREFIX = "LANG_LEARN_FF_"


def _truthy(raw: str) -> bool:
    return raw.strip().lower() in {"1", "true", "yes", "on"}


class FeatureFlags:
    """Снимок включённых фич (иммутабельный)."""

    __slots__ = ("_enabled",)

    def __init__(self, enabled: frozenset[str]) -> None:
        self._enabled = enabled

    def is_enabled(self, name: str) -> bool:
        """Проверка флага; неизвестные имена дают False."""
        return name in KNOWN_FEATURE_FLAGS and name in self._enabled

    @property
    def enabled_names(self) -> frozenset[str]:
        """Множество включённых известных флагов."""
        return self._enabled

    def as_dict(self) -> dict[str, bool]:
        """Все известные флаги с булевыми значениями (удобно для JSON/логов)."""
        return {name: name in self._enabled for name in sorted(KNOWN_FEATURE_FLAGS)}


def load_feature_flags(
    environ: Mapping[str, str] | None = None,
) -> FeatureFlags:
    """
    Прочитать ``LANG_LEARN_FF_<FLAG>=1|true|…`` из ``environ``.

    По умолчанию — ``os.environ``. Неизвестные ``<FLAG>`` пропускаются.
    """
    import os

    src = environ if environ is not None else os.environ
    enabled: set[str] = set()
    for key, val in src.items():
        if not key.startswith(_ENV_PREFIX):
            continue
        name = key[len(_ENV_PREFIX) :].lower()
        if name not in KNOWN_FEATURE_FLAGS:
            continue
        if _truthy(val):
            enabled.add(name)
    return FeatureFlags(frozenset(enabled))
