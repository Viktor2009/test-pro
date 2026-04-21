"""Проверка Pydantic-схем аудио-слоя."""

import pytest
from pydantic import ValidationError

from lang_learn.schemas.audio import (
    AudioFormat,
    STTRequest,
    STTResult,
    TTSRequest,
    TTSResult,
)


def test_tts_request_valid() -> None:
    req = TTSRequest(text="Hello", language="en-US", speed=1.0)
    assert req.audio_format == AudioFormat.WAV


def test_tts_request_speed_bounds() -> None:
    with pytest.raises(ValidationError):
        TTSRequest(text="x", language="en", speed=0.1)


def test_stt_request_non_empty_audio() -> None:
    with pytest.raises(ValidationError):
        STTRequest(audio=b"")


def test_stt_request_vad_and_prompt_optional() -> None:
    req = STTRequest(
        audio=b"x",
        language="en-US",
        vad_filter=False,
        initial_prompt="ay apple",
    )
    assert req.vad_filter is False
    assert req.initial_prompt == "ay apple"


def test_stt_result_confidence_bounds() -> None:
    with pytest.raises(ValidationError):
        STTResult(text="a", confidence=1.5)


def test_tts_result_frozen() -> None:
    res = TTSResult(audio=b"x", format=AudioFormat.PCM)
    with pytest.raises(ValidationError):
        res.format = AudioFormat.MP3  # type: ignore[misc]
