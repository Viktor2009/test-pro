"""Огибающая WAV для отрисовки волны (без matplotlib)."""

from __future__ import annotations

import wave


def wav_to_envelope_xy(
    wav: bytes,
    *,
    max_points: int = 700,
) -> tuple[list[float], list[float], float, float]:
    """
    Сжать моно int16 WAV до огибающей для графика.

    Returns:
        ``(x_seconds, y_0..1, duration_s, peak_linear)``, где ``peak_linear`` —
        максимум огибающей по чанкам до нормировки (для общей шкалы с эталоном).
        При ошибке или без numpy — пустые списки и два нуля.
    """
    try:
        import numpy as np
    except ImportError:
        return [], [], 0.0, 0.0

    try:
        from lang_learn.audio_io.wav_utils import read_wav_int16_mono
    except ImportError:
        return [], [], 0.0, 0.0

    try:
        pcm, sr = read_wav_int16_mono(wav)
    except (ValueError, OSError, EOFError, wave.Error):
        return [], [], 0.0, 0.0

    if sr <= 0 or len(pcm) < 2:
        return [], [], 0.0, 0.0

    samples = np.frombuffer(pcm, dtype=np.int16).astype(np.float32)
    n = int(samples.shape[0])
    duration = n / float(sr)
    m = int(max(2, min(max_points, n)))
    chunk = max(1, n // m)
    ys_list: list[float] = []
    for i in range(m):
        lo = i * chunk
        hi = min(n, (i + 1) * chunk)
        seg = samples[lo:hi]
        ys_list.append(float(np.max(np.abs(seg))))
    ys = np.array(ys_list, dtype=np.float64)
    peak = float(np.max(ys)) if ys.size else 0.0
    if peak > 1e-9:
        ys = ys / peak
    else:
        ys = np.zeros_like(ys)
    xs = np.linspace(0.0, duration, num=m, dtype=np.float64)
    return xs.tolist(), ys.tolist(), duration, peak
