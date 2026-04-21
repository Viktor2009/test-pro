"""Модуль озвучки pyttsx3 (без реального вывода звука в CI)."""

from lang_learn.audio_io.pyttsx3_speak_chunks import speak_pyttsx3_chunks


def test_speak_pyttsx3_chunks_empty_returns_message() -> None:
    assert speak_pyttsx3_chunks([]) == "Нет фрагментов для озвучки."
