"""План shadowing."""

from lang_learn.learning.shadowing import build_shadowing_plan


def test_shadowing_slower_has_longer_pause() -> None:
    slow = build_shadowing_plan("one two three four", tempo="slow")
    fast = build_shadowing_plan("one two three four", tempo="fast")
    assert (
        slow.suggested_pause_after_reference_ms
        > fast.suggested_pause_after_reference_ms
    )
    assert slow.suggested_target_duration_ms >= fast.suggested_target_duration_ms
