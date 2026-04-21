"""Логика обрезки огибающей для сравнения волн."""

from __future__ import annotations

from lang_learn.gui.waveform_compare import WaveformCompareFrame


def test_trim_leading_silence_moves_start_to_zero() -> None:
    xs = [0.0, 0.1, 0.2, 0.3]
    ys = [0.01, 0.02, 0.09, 0.5]
    dur = 0.3
    xt, yt, dtr = WaveformCompareFrame._trim_leading_silence(xs, ys, dur)
    assert xt[0] == 0.0
    assert abs(xt[-1] - (0.3 - 0.2)) < 1e-9
    assert yt[0] == 0.09
    assert yt[-1] == 0.5
    assert abs(dtr - 0.1) < 1e-9


def test_cap_envelope_duration_truncates_user_window() -> None:
    xs = [0.0, 1.0, 2.0, 3.0, 4.0]
    ys = [0.2, 0.3, 0.4, 0.5, 0.6]
    env = (xs, ys, 4.0, 5000.0)
    xc, yc, dc, pk = WaveformCompareFrame._cap_envelope_duration(env, 2.5)
    assert xc == [0.0, 1.0, 2.0]
    assert yc == [0.2, 0.3, 0.4]
    assert dc == 2.5
    assert pk == 5000.0


def test_trim_no_change_if_loud_from_start() -> None:
    xs = [0.0, 0.05]
    ys = [0.2, 0.4]
    dur = 0.05
    xt, yt, dtr = WaveformCompareFrame._trim_leading_silence(xs, ys, dur)
    assert xt == xs
    assert yt == ys
    assert dtr == dur
