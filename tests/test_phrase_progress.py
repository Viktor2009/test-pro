"""Прогресс по фразе до/после."""

from lang_learn.learning.phrase_progress import (
    record_composite_score,
    summarize_phrase_progress,
)
from lang_learn.schemas.speech_quality import PhraseScoreLog


def test_record_and_summarize_improvement() -> None:
    log = PhraseScoreLog(phrase_id="p1", composite_scores=(0.4, 0.45, 0.62))
    out = summarize_phrase_progress(log)
    assert "Прогресс" in out or "прирост" in out


def test_record_composite_score_clamps() -> None:
    log = PhraseScoreLog(phrase_id="p2", composite_scores=(0.5,))
    log2 = record_composite_score(log, 1.5)
    assert log2.composite_scores[-1] == 1.0
