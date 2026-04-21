"""Утилиты WAV без optional extra."""

from lang_learn.audio_io.wav_utils import (
    read_wav_int16_mono,
    wav_duration_ms,
    wav_int16_mono_rms_dbfs,
    write_wav_int16_mono,
)


def test_write_read_roundtrip() -> None:
    pcm = (30000).to_bytes(2, "little", signed=True) * 8000
    wav = write_wav_int16_mono(pcm, 8000)
    out, sr = read_wav_int16_mono(wav)
    assert sr == 8000
    assert out == pcm


def test_wav_duration_ms() -> None:
    pcm = b"\x00\x00" * 16000
    wav = write_wav_int16_mono(pcm, 16000)
    assert wav_duration_ms(wav) == 1000


def test_wav_int16_mono_rms_dbfs_silence_vs_tone() -> None:
    silence = write_wav_int16_mono(b"\x00\x00" * 8000, 8000)
    assert wav_int16_mono_rms_dbfs(silence) == -96.0
    pcm = (10000).to_bytes(2, "little", signed=True) * 8000
    loud = write_wav_int16_mono(pcm, 8000)
    db = wav_int16_mono_rms_dbfs(loud)
    assert db is not None
    assert db > -40.0
