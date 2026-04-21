"""Логика панели Pre-A0 без tkinter."""

from lang_learn.gui import pre_a0_alphabet_voice_flow as alphabet_voice_flow
from lang_learn.gui.pre_a0_alphabet_voice_flow import (
    VoicePhaseTiming,
    pick_alphabet_voice_flow,
    register_alphabet_voice_flow,
)
from lang_learn.gui.pre_a0_lesson import (
    _LETTER_NAME_TTS,
    _reference_for_ui_score,
    english_tts_chunks,
)
from lang_learn.learning.pre_a0_engine import short_grapheme_answer_matches
from lang_learn.schemas.learning import ExercisePayload
from lang_learn.schemas.pre_a0 import ExerciseKind


def test_reference_for_ui_score_recognize_prefers_metadata() -> None:
    ex = ExercisePayload(
        exercise_id="prea0.en.z.pick",
        kind=ExerciseKind.RECOGNIZE_LETTER.value,
        reference_text="Z",
        metadata={"correct": "M"},
    )
    assert _reference_for_ui_score(ex) == "M"


def test_reference_for_ui_score_listen_uses_reference_text() -> None:
    ex = ExercisePayload(
        exercise_id="prea0.en.a.listen",
        kind=ExerciseKind.LISTEN_REPEAT.value,
        reference_text="A apple",
        metadata={"grapheme": "A"},
    )
    assert _reference_for_ui_score(ex) == "A apple"


def test_tts_chunks_letter_listen_name_then_word_not_sentence() -> None:
    ex = ExercisePayload(
        exercise_id="prea0.en.a.listen",
        kind=ExerciseKind.LISTEN_REPEAT.value,
        reference_text="A apple",
        metadata={"letter_id": "en.a", "grapheme": "A"},
    )
    chunks = english_tts_chunks(ex)
    assert chunks == ["ay", "apple"]


def test_tts_chunks_read_single_letter_short_only() -> None:
    ex = ExercisePayload(
        exercise_id="prea0.en.a.read",
        kind=ExerciseKind.READ_ALOUD_COMPARE.value,
        reference_text="A",
        metadata={"letter_id": "en.a", "grapheme": "A"},
    )
    assert english_tts_chunks(ex) == ["ay"]


def test_tts_chunks_cluster_listen_two_parts() -> None:
    ex = ExercisePayload(
        exercise_id="prea0.en.ch.listen",
        kind=ExerciseKind.LISTEN_REPEAT.value,
        reference_text="ch chair",
        metadata={"cluster_id": "en.ch", "grapheme": "ch"},
    )
    assert english_tts_chunks(ex) == ["ch", "chair"]


def test_voice_flow_matches_listen_repeat_letter() -> None:
    ex = ExercisePayload(
        exercise_id="prea0.en.a.listen",
        kind=ExerciseKind.LISTEN_REPEAT.value,
        reference_text="A apple",
        metadata={"letter_id": "en.a", "grapheme": "A"},
    )
    flow = pick_alphabet_voice_flow(ex)
    assert flow is not None
    assert flow.timing(ex).record_duration_s == 5.0


def test_voice_flow_skips_read_step() -> None:
    ex = ExercisePayload(
        exercise_id="prea0.en.a.read",
        kind=ExerciseKind.READ_ALOUD_COMPARE.value,
        reference_text="A",
        metadata={"letter_id": "en.a", "grapheme": "A"},
    )
    flow = pick_alphabet_voice_flow(ex)
    assert flow is not None
    assert flow.timing(ex).record_duration_s == 4.0


def test_register_voice_flow_prepended() -> None:
    class _CustomFlow:
        def matches(self, ex: ExercisePayload) -> bool:
            return str(ex.exercise_id) == "custom.test"

        def timing(self, ex: ExercisePayload) -> VoicePhaseTiming:
            _ = ex
            return VoicePhaseTiming(
                silence_after_reference_s=1.0,
                record_duration_s=3.0,
            )

    custom = _CustomFlow()
    before = len(alphabet_voice_flow._VOICE_FLOWS)
    register_alphabet_voice_flow(custom)
    try:
        ex = ExercisePayload(
            exercise_id="custom.test",
            kind=ExerciseKind.READ_ALOUD_COMPARE.value,
            reference_text="X",
            metadata={},
        )
        assert pick_alphabet_voice_flow(ex) is custom
    finally:
        alphabet_voice_flow._VOICE_FLOWS.remove(custom)
        assert len(alphabet_voice_flow._VOICE_FLOWS) == before


def test_short_grapheme_requires_exact_length_for_letter() -> None:
    ex = ExercisePayload(
        exercise_id="prea0.en.a.listen",
        kind=ExerciseKind.LISTEN_REPEAT.value,
        reference_text="A apple",
        metadata={"letter_id": "en.a", "grapheme": "A"},
    )
    assert short_grapheme_answer_matches(ex, "A")
    assert short_grapheme_answer_matches(ex, "a")
    assert not short_grapheme_answer_matches(ex, "AA")
    assert not short_grapheme_answer_matches(ex, "Aa")


def test_all_latin_letters_have_tts_token() -> None:
    for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        assert c in _LETTER_NAME_TTS
        assert _LETTER_NAME_TTS[c]
