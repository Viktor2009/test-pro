"""Базовая оценка произношения (текстовая похожесть)."""

from lang_learn.learning.pronunciation import (
    missing_key_graphemes,
    normalize_utterance,
    utterance_similarity,
)


def test_normalize_utterance() -> None:
    assert normalize_utterance("  Hello!  ") == "hello"


def test_utterance_similarity_identical() -> None:
    assert utterance_similarity("Apple", "apple") == 1.0


def test_utterance_similarity_partial() -> None:
    s = utterance_similarity("apple", "aple")
    assert 0.5 < s < 1.0


def test_missing_key_graphemes() -> None:
    assert missing_key_graphemes("pple", ["A"]) == ["A"]
    assert missing_key_graphemes("apple", ["A"]) == []
