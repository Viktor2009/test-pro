"""Чтение/запись моно PCM16 WAV без внешних зависимостей."""

from __future__ import annotations

import array
import io
import math
import wave


def write_wav_int16_mono(pcm_s16le: bytes, sample_rate_hz: int) -> bytes:
    """
    Собрать WAV (моно, 16 бит little-endian) из сырых PCM-кадров.

    Args:
        pcm_s16le: сырые кадры ``n * 2`` байт.
        sample_rate_hz: частота дискретизации.
    """
    if sample_rate_hz < 8000 or sample_rate_hz > 48000:
        msg = f"sample_rate_hz out of range: {sample_rate_hz}"
        raise ValueError(msg)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate_hz)
        wf.writeframes(pcm_s16le)
    return buf.getvalue()


def read_wav_int16_mono(data: bytes) -> tuple[bytes, int]:
    """
    Прочитать моно PCM16 из WAV.

    Returns:
        Кортеж ``(pcm_s16le, sample_rate_hz)``. Если в файле несколько
        каналов, для этапа 1 выбрасывается ``ValueError`` (нужен моно).
    """
    with wave.open(io.BytesIO(data), "rb") as wf:
        if wf.getnchannels() != 1:
            msg = "expected mono WAV"
            raise ValueError(msg)
        if wf.getsampwidth() != 2:
            msg = "expected 16-bit WAV"
            raise ValueError(msg)
        sr = wf.getframerate()
        pcm = wf.readframes(wf.getnframes())
    return pcm, sr


def wav_duration_ms(data: bytes) -> int:
    """Длительность WAV в миллисекундах (моно 16 бит)."""
    with wave.open(io.BytesIO(data), "rb") as wf:
        frames = wf.getnframes()
        sr = wf.getframerate()
    if sr <= 0:
        return 0
    return int(round(1000.0 * frames / float(sr)))


def wav_int16_mono_rms_dbfs(data: bytes) -> float | None:
    """
    Среднеквадратичный уровень моно PCM16 WAV в dBFS (относительно полной шкалы).

    Returns:
        dBFS или ``None``, если сигнал отсутствует / не моно 16 бит.
    """
    try:
        pcm, _sr = read_wav_int16_mono(data)
    except (ValueError, wave.Error):
        return None
    if len(pcm) < 2:
        return None
    samples = array.array("h")
    samples.frombytes(pcm)
    n = len(samples)
    if n == 0:
        return None
    acc = sum(s * s for s in samples)
    rms = math.sqrt(acc / float(n))
    if rms <= 0.0:
        return -96.0
    return 20.0 * math.log10(rms / 32768.0)
