"""Воспроизведение WAV через PortAudio."""

from __future__ import annotations

from lang_learn.audio_io.wav_utils import read_wav_int16_mono


def play_wav_bytes(data: bytes) -> None:
    """
    Воспроизвести моно 16-bit WAV.

    Raises:
        ImportError: без ``sounddevice``/``numpy`` (extra ``audio``).
    """
    try:
        import numpy as np
        import sounddevice as sd
    except ImportError as exc:
        msg = (
            "play_wav_bytes requires optional dependencies "
            "'numpy' and 'sounddevice'. Install: pip install -e \".[audio]\""
        )
        raise ImportError(msg) from exc

    pcm, sr = read_wav_int16_mono(data)
    samples = np.frombuffer(pcm, dtype=np.int16).astype(np.float32) / 32768.0
    sd.play(samples, sr)
    sd.wait()
