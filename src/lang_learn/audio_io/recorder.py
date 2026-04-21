"""Запись с микрофона в WAV (моно PCM16)."""

from __future__ import annotations

from typing import Any

from lang_learn.audio_io.wav_utils import write_wav_int16_mono


def _resolve_input_device_index(sd: Any, explicit: int | None) -> int:
    """
    Подобрать индекс входного устройства для ``sd.rec``.

    Явный индекс обязан существовать. Для ``None`` используется системный
    default; если он недоступен (часто даёт ``-1`` и PortAudioError),
    берётся первое устройство с ``max_input_channels > 0``.
    """
    if explicit is not None:
        if explicit < 0:
            msg = "device must be >= 0 or None"
            raise ValueError(msg)
        sd.query_devices(explicit)
        return explicit

    default_pair = sd.default.device
    if isinstance(default_pair, (list, tuple)) and len(default_pair) >= 1:
        inp = default_pair[0]
        if inp is not None and inp >= 0:
            sd.query_devices(int(inp))
            return int(inp)

    devices = sd.query_devices()
    for i, raw in enumerate(devices):
        if int(raw.get("max_input_channels", 0)) > 0:
            return i

    msg = (
        "Не найдено устройство ввода (микрофон): возможно, микрофон не подключён "
        "или не установлен; иначе default недоступен или нет каналов ввода. "
        "Проверьте подключение, драйверы и «Параметры конфиденциальности → Микрофон» "
        "в Windows. Список устройств: python -m lang_learn devices"
    )
    raise RuntimeError(msg)


class MicrophoneRecorder:
    """
    Запись с устройства ввода по умолчанию (или выбранного индекса).

    Требует optional extra ``audio`` (``sounddevice``, ``numpy``).
    """

    def __init__(
        self,
        *,
        sample_rate_hz: int = 16_000,
        device: int | None = None,
    ) -> None:
        if sample_rate_hz < 8000 or sample_rate_hz > 48000:
            msg = f"sample_rate_hz out of range: {sample_rate_hz}"
            raise ValueError(msg)
        self._sr = sample_rate_hz
        self._device = device

    def record_seconds(self, duration_s: float) -> bytes:
        """
        Записать ``duration_s`` секунд и вернуть WAV (моно int16).

        Raises:
            ImportError: без установленных ``sounddevice``/``numpy``.
            ValueError: некорректная длительность.
        """
        if duration_s <= 0 or duration_s > 300:
            msg = "duration_s must be in (0, 300]"
            raise ValueError(msg)
        try:
            import numpy as np
            import sounddevice as sd
        except ImportError as exc:
            msg = (
                "MicrophoneRecorder requires optional dependencies "
                "'numpy' and 'sounddevice'. Install: pip install -e \".[audio]\""
            )
            raise ImportError(msg) from exc

        n_frames = int(round(self._sr * duration_s))
        device_index = _resolve_input_device_index(sd, self._device)
        recording = sd.rec(
            n_frames,
            samplerate=self._sr,
            channels=1,
            dtype="float32",
            device=device_index,
        )
        sd.wait()
        mono = np.clip(recording[:, 0] * 32767.0, -32768.0, 32767.0).astype(
            np.int16,
        )
        return write_wav_int16_mono(mono.tobytes(), self._sr)
