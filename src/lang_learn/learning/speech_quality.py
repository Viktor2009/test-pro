"""Многокомпонентная оценка произношения по эталону и гипотезе (текст / STT)."""

from __future__ import annotations

import difflib
import math

from lang_learn.learning import pronunciation as pron
from lang_learn.schemas.speech_quality import (
    PronunciationReport,
    PronunciationScores,
    WordAlignmentIssue,
)


def _tokenize_words(text: str) -> list[str]:
    return [w for w in pron.normalize_utterance(text).split() if w]


def _word_set_accuracy(reference: str, hypothesis: str) -> float:
    """Jaccard по множеству слов (грубая word accuracy)."""
    a = set(_tokenize_words(reference))
    b = set(_tokenize_words(hypothesis))
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0


def _word_alignment_issues(
    reference: str,
    hypothesis: str,
) -> tuple[WordAlignmentIssue, ...]:
    """Поиск слов эталона без достаточно похожего совпадения в гипотезе."""
    rw = _tokenize_words(reference)
    hw = _tokenize_words(hypothesis)
    used: set[int] = set()
    issues: list[WordAlignmentIssue] = []
    for w in rw:
        best_j: int | None = None
        best_sim = 0.0
        for j, h in enumerate(hw):
            if j in used:
                continue
            sim = difflib.SequenceMatcher(None, w, h).ratio()
            if sim > best_sim:
                best_sim = sim
                best_j = j
        if best_sim >= 0.82 and best_j is not None:
            used.add(best_j)
            continue
        observed = hw[best_j] if best_j is not None else None
        issues.append(
            WordAlignmentIssue(
                reference_word=w,
                observed=observed,
                hint=_articulation_hint(w, observed),
            ),
        )
    return tuple(issues)


def _articulation_hint(ref_word: str, observed: str | None) -> str:
    if observed:
        return (
            f"Сравните «{ref_word}» с тем, что распознано («{observed}»): "
            "растяните ударный слог, смягчите конец слова."
        )
    return (
        f"Слово «{ref_word}» не найдено в ответе: произнесите его отдельно, "
        "по слогам, затем в составе фразы."
    )


def _text_length_fluency(reference: str, hypothesis: str) -> float:
    """Прокси беглости по длине текста (без разметки пауз из аудио)."""
    r = pron.normalize_utterance(reference)
    h = pron.normalize_utterance(hypothesis)
    if not r and not h:
        return 1.0
    if not r or not h:
        return 0.0
    lr, lh = len(r), len(h)
    ratio = min(lr, lh) / max(lr, lh)
    rw, hw = len(_tokenize_words(r)), len(_tokenize_words(h))
    if max(rw, hw) == 0:
        return float(ratio)
    wratio = min(rw, hw) / max(rw, hw)
    return float(0.5 * ratio + 0.5 * wratio)


def _duration_fluency(
    reference_ms: int | None,
    hypothesis_ms: int | None,
) -> float | None:
    """Оценка по соотношению длительностей записей (если известны)."""
    if reference_ms is None or hypothesis_ms is None:
        return None
    if reference_ms <= 0 or hypothesis_ms <= 0:
        return None
    ratio = hypothesis_ms / reference_ms
    # около 1 — хорошо; сильный перекос снижает балл
    dev = abs(math.log(max(ratio, 1e-3)))
    return float(max(0.0, 1.0 - min(dev / 1.5, 1.0)))


def _fluency(
    reference: str,
    hypothesis: str,
    reference_ms: int | None,
    hypothesis_ms: int | None,
) -> float:
    text_f = _text_length_fluency(reference, hypothesis)
    dur_f = _duration_fluency(reference_ms, hypothesis_ms)
    if dur_f is None:
        return text_f
    return float(0.55 * text_f + 0.45 * dur_f)


def _composite(intel: float, word_acc: float, fluency: float) -> float:
    return float(0.4 * intel + 0.35 * word_acc + 0.25 * fluency)


def _collect_tips(
    issues: tuple[WordAlignmentIssue, ...],
    composite: float,
) -> tuple[str, ...]:
    tips: list[str] = []
    for issue in issues[:5]:
        if issue.hint:
            tips.append(issue.hint)
    if composite < 0.55:
        tips.append(
            "Общая понятность низкая: замедлитесь, проговаривайте концовки слов "
            "и делайте микропаузу между словами.",
        )
    # уникальные, порядок сохранён
    seen: set[str] = set()
    out: list[str] = []
    for t in tips:
        if t not in seen:
            seen.add(t)
            out.append(t)
    return tuple(out)


def analyze_pronunciation(
    reference: str,
    hypothesis: str,
    *,
    reference_audio_duration_ms: int | None = None,
    hypothesis_audio_duration_ms: int | None = None,
) -> PronunciationReport:
    """
    Построить отчёт: intelligibility ≈ общая близость строк,
    word_accuracy — по словам, fluency — длина текста и (если есть) длительности.
    """
    ref = reference.strip()
    hyp = hypothesis.strip()
    if not ref:
        msg = "reference must be non-empty"
        raise ValueError(msg)
    intel = pron.utterance_similarity(ref, hyp) if hyp else 0.0
    word_acc = _word_set_accuracy(ref, hyp)
    flu = _fluency(ref, hyp, reference_audio_duration_ms, hypothesis_audio_duration_ms)
    comp = _composite(intel, word_acc, flu)
    if hyp:
        issues = _word_alignment_issues(ref, hyp)
    else:
        issues = tuple(
            WordAlignmentIssue(
                reference_word=w,
                observed=None,
                hint=_articulation_hint(w, None),
            )
            for w in _tokenize_words(ref)
        )
    tips = _collect_tips(issues, comp)
    scores = PronunciationScores(
        intelligibility=intel,
        word_accuracy=word_acc,
        fluency=flu,
        composite=comp,
    )
    return PronunciationReport(
        reference_text=ref,
        hypothesis_text=hyp,
        scores=scores,
        word_issues=issues,
        articulation_tips=tips,
        reference_echo_text=ref,
    )
