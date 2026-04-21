"""Многокомпонентная оценка произношения."""

from lang_learn.learning.speech_quality import analyze_pronunciation


def test_analyze_close_match_high_scores() -> None:
    rep = analyze_pronunciation(
        "I need a taxi to the hotel.",
        "I need a taxi to the hotel.",
        reference_audio_duration_ms=3000,
        hypothesis_audio_duration_ms=3100,
    )
    assert rep.scores.composite >= 0.85
    assert not rep.word_issues


def test_analyze_poor_match_and_issues() -> None:
    rep = analyze_pronunciation(
        "Where is the gate?",
        "Wear is da gait?",
    )
    assert rep.scores.word_accuracy < 0.8
    assert rep.word_issues


def test_empty_hypothesis() -> None:
    rep = analyze_pronunciation("Hello there", "")
    assert rep.scores.intelligibility == 0.0
    assert rep.word_issues
