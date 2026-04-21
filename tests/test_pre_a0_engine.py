"""PreA0LessonEngine: очередь и оценка."""

from lang_learn.learning.course_loader import load_packaged_en_sample
from lang_learn.learning.pre_a0_engine import PreA0LessonEngine
from lang_learn.schemas.learning import AttemptRecord, LessonContext


def test_empty_submit_does_not_stack_repeats() -> None:
    """Пустой ввод не должен трижды класть то же упражнение в стек повтора."""
    eng = PreA0LessonEngine(load_packaged_en_sample(), accept_threshold=0.55)
    uid = "u-empty"
    ctx = LessonContext(user_id=uid)
    ex1 = eng.next_exercise(ctx)
    for i in range(3):
        fb = eng.submit_attempt(
            AttemptRecord(
                attempt_id=f"empty-{i}",
                user_id=uid,
                exercise_id=ex1.exercise_id,
                transcript="",
            ),
        )
        assert fb.accepted is False
    ex2 = eng.next_exercise(ctx)
    assert ex2.exercise_id != ex1.exercise_id


def test_listen_repeat_accepts_single_letter_case_insensitive() -> None:
    eng = PreA0LessonEngine(load_packaged_en_sample(), accept_threshold=0.55)
    uid = "u-letter"
    ctx = LessonContext(user_id=uid)
    ex = eng.next_exercise(ctx)
    assert ex.exercise_id == "prea0.en.a.listen"
    for text in ("A", "a"):
        fb = eng.submit_attempt(
            AttemptRecord(
                attempt_id=f"att-{text}",
                user_id=uid,
                exercise_id=ex.exercise_id,
                transcript=text,
            ),
        )
        assert fb.accepted is True, text


def test_listen_repeat_rejects_two_letters() -> None:
    eng = PreA0LessonEngine(load_packaged_en_sample(), accept_threshold=0.55)
    uid = "u-two"
    ctx = LessonContext(user_id=uid)
    ex = eng.next_exercise(ctx)
    assert ex.exercise_id == "prea0.en.a.listen"
    for bad in ("AA", "Aa", "aA", "AB"):
        fb = eng.submit_attempt(
            AttemptRecord(
                attempt_id=f"att-{bad}",
                user_id=uid,
                exercise_id=ex.exercise_id,
                transcript=bad,
            ),
        )
        assert fb.accepted is False, bad


def test_recognize_letter_accepts_lowercase_once() -> None:
    eng = PreA0LessonEngine(load_packaged_en_sample(), accept_threshold=0.55)
    uid = "u-low"
    ctx = LessonContext(user_id=uid)
    eng.next_exercise(ctx)
    eng.next_exercise(ctx)
    ex = eng.next_exercise(ctx)
    assert ex.exercise_id == "prea0.en.a.pick"
    fb = eng.submit_attempt(
        AttemptRecord(
            attempt_id="att-a",
            user_id=uid,
            exercise_id=ex.exercise_id,
            transcript="a",
        ),
    )
    assert fb.accepted is True


def test_recognize_letter_accepts_repeated_same_letter_from_stt() -> None:
    eng = PreA0LessonEngine(load_packaged_en_sample(), accept_threshold=0.55)
    uid = "u-stt-repeat"
    ctx = LessonContext(user_id=uid)
    eng.next_exercise(ctx)
    eng.next_exercise(ctx)
    ex = eng.next_exercise(ctx)
    assert ex.exercise_id == "prea0.en.a.pick"
    fb = eng.submit_attempt(
        AttemptRecord(
            attempt_id="att-a3",
            user_id=uid,
            exercise_id=ex.exercise_id,
            transcript="A. A. A.",
        ),
    )
    assert fb.accepted is True


def test_recognize_letter_rejects_two_characters() -> None:
    eng = PreA0LessonEngine(load_packaged_en_sample(), accept_threshold=0.55)
    uid = "u-pick"
    ctx = LessonContext(user_id=uid)
    eng.next_exercise(ctx)
    eng.next_exercise(ctx)
    ex = eng.next_exercise(ctx)
    assert ex.exercise_id == "prea0.en.a.pick"
    fb = eng.submit_attempt(
        AttemptRecord(
            attempt_id="att-aa",
            user_id=uid,
            exercise_id=ex.exercise_id,
            transcript="Aa",
        ),
    )
    assert fb.accepted is False
    assert "одна" in fb.summary.lower()


def test_engine_advances_and_repeats_on_failure() -> None:
    eng = PreA0LessonEngine(load_packaged_en_sample(), accept_threshold=0.9)
    uid = "u-test"
    ctx = LessonContext(user_id=uid)
    ex1 = eng.next_exercise(ctx)
    fb_bad = eng.submit_attempt(
        AttemptRecord(
            attempt_id="att-1",
            user_id=uid,
            exercise_id=ex1.exercise_id,
            transcript="zzz",
        ),
    )
    assert fb_bad.accepted is False
    ex_repeat = eng.next_exercise(ctx)
    assert ex_repeat.exercise_id == ex1.exercise_id
    ref = (ex1.reference_text or "").strip()
    fb_ok = eng.submit_attempt(
        AttemptRecord(
            attempt_id="att-2",
            user_id=uid,
            exercise_id=ex1.exercise_id,
            transcript=ref,
        ),
    )
    assert fb_ok.accepted is True
    ex2 = eng.next_exercise(ctx)
    assert ex2.exercise_id != ex1.exercise_id


def test_seek_user_to_exercise_and_menu_entries() -> None:
    eng = PreA0LessonEngine(load_packaged_en_sample(), accept_threshold=0.55)
    uid = "u-seek"
    ctx = LessonContext(user_id=uid)
    entries = eng.exercise_menu_entries()
    assert entries[0][0] == "prea0.en.a.listen"
    assert "слушай" in entries[0][1].lower()

    eng.next_exercise(ctx)
    eng.next_exercise(ctx)
    assert eng.seek_user_to_exercise(uid, "prea0.en.z.listen") is True
    ex = eng.next_exercise(ctx)
    assert ex.exercise_id == "prea0.en.z.listen"

    assert eng.seek_user_to_exercise(uid, "no-such-id") is False
