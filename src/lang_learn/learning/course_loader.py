"""Загрузка курсов Pre-A0 из JSON."""

from __future__ import annotations

import json
from importlib import resources

from lang_learn.schemas.pre_a0 import PreA0Course


def load_pre_a0_course_bytes(data: bytes) -> PreA0Course:
    """Разобрать JSON курса в ``PreA0Course``."""
    raw = json.loads(data.decode("utf-8"))
    return PreA0Course.model_validate(raw)


def load_packaged_en_sample() -> PreA0Course:
    """Загрузить встроенный пример ``en_sample.json``."""
    from lang_learn.data import pre_a0 as pre_a0_data

    path = resources.files(pre_a0_data).joinpath("en_sample.json")
    return load_pre_a0_course_bytes(path.read_bytes())
