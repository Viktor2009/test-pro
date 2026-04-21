"""Огибающая WAV для графика."""

from lang_learn.audio_io.wav_envelope import wav_to_envelope_xy
from lang_learn.audio_io.wav_utils import write_wav_int16_mono


def test_wav_to_envelope_xy_nonzero_for_tone() -> None:
    import array

    samples = array.array("h", [0, 5000, -5000, 8000, 0] * 400)
    wav = write_wav_int16_mono(samples.tobytes(), 16_000)
    xs, ys, dur, peak = wav_to_envelope_xy(wav, max_points=50)
    assert dur > 0
    assert len(xs) == len(ys) == 50
    assert max(ys) <= 1.0 + 1e-6
    assert min(ys) >= 0.0
    assert peak >= 8000.0 * 0.99


def test_wav_to_envelope_xy_empty_on_invalid() -> None:
    xs, ys, dur, peak = wav_to_envelope_xy(b"not a wav")
    assert xs == [] and ys == [] and dur == 0.0 and peak == 0.0
