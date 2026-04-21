"""Сравнение прогресса «до/после» по трудным фразам."""

from __future__ import annotations

from lang_learn.schemas.speech_quality import PhraseScoreLog


def record_composite_score(log: PhraseScoreLog, score: float) -> PhraseScoreLog:
    """Добавить значение composite (ожидается ``[0, 1]``)."""
    s = max(0.0, min(1.0, float(score)))
    return log.model_copy(update={"composite_scores": log.composite_scores + (s,)})


def summarize_phrase_progress(log: PhraseScoreLog) -> str:
    """Краткий текст для пользователя: динамика по последним попыткам."""
    vals = log.composite_scores
    if len(vals) < 2:
        return "Нужно минимум две попытки, чтобы сравнить «до» и «после»."
    first, last = vals[0], vals[-1]
    delta = last - first
    if delta > 0.08:
        return (
            f"Прогресс по фразе «{log.phrase_id}»: прирост {delta:.2f} "
            f"(было {first:.2f}, стало {last:.2f})."
        )
    if delta < -0.05:
        return (
            f"По фразе «{log.phrase_id}» балл снизился на {-delta:.2f}. "
            "Сделайте shadowing на медленном темпе и короче фразу."
        )
    return (
        f"По фразе «{log.phrase_id}» стабильно около {last:.2f}; можно усложнить темп."
    )
