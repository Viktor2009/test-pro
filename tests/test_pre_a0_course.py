"""Загрузка и валидация курса Pre-A0."""

from lang_learn.learning.course_loader import load_packaged_en_sample
from lang_learn.schemas.pre_a0 import PreA0Course


def test_load_packaged_en_sample() -> None:
    course = load_packaged_en_sample()
    assert course.language == "en-US"
    assert len(course.letters) >= 26
    assert course.letters[0].grapheme == "A"


def test_course_roundtrip_json() -> None:
    from lang_learn.learning.course_loader import load_pre_a0_course_bytes

    c1 = load_packaged_en_sample()
    raw = c1.model_dump_json().encode("utf-8")
    c2 = load_pre_a0_course_bytes(raw)
    assert isinstance(c2, PreA0Course)
    assert c2.title == c1.title
