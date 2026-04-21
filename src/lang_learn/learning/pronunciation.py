"""Базовая оценка близости произнесённого текста к эталону (этап 2, MVP)."""

from __future__ import annotations

import difflib
import re
from collections.abc import Iterable

_NON_WORD = re.compile(r"[^\w\s]", re.UNICODE)
_WS = re.compile(r"\s+")


def normalize_utterance(text: str) -> str:
    """Нижний регистр, убрать пунктуацию, схлопнуть пробелы."""
    t = text.lower().strip()
    t = _NON_WORD.sub("", t)
    t = _WS.sub(" ", t)
    return t.strip()


def utterance_similarity(reference: str, hypothesis: str) -> float:
    """
    Оценка похожести строк в ``[0, 1]`` (SequenceMatcher по нормализованному тексту).

    Подходит для коротких ответов (буква, слово, фраза) без фонетического разбора.
    """
    a = normalize_utterance(reference)
    b = normalize_utterance(hypothesis)
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return float(difflib.SequenceMatcher(None, a, b).ratio())


def missing_key_graphemes(
    hypothesis: str,
    keys: Iterable[str],
) -> list[str]:
    """
    Какие ключевые графемы не найдены в ответе (грубое вхождение подстроки).

    Сравнение по нормализованному тексту без пробелов в гипотезе.
    """
    h = normalize_utterance(hypothesis).replace(" ", "")
    missing: list[str] = []
    for key in keys:
        k = normalize_utterance(key).replace(" ", "")
        if not k:
            continue
        if k not in h:
            missing.append(key)
    return missing
