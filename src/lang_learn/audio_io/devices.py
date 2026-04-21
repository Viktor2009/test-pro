"""Список аудиоустройств (вход/выход)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AudioDeviceInfo:
    """Краткое описание устройства для диагностики UI."""

    index: int
    name: str
    max_input_channels: int
    max_output_channels: int
    default_samplerate: float | None


def list_audio_devices() -> list[AudioDeviceInfo]:
    """
    Вернуть список устройств PortAudio (через ``sounddevice``).

    Raises:
        ImportError: если не установлен extra ``audio`` (``sounddevice``).
    """
    try:
        import sounddevice as sd
    except ImportError as exc:  # pragma: no cover - tested via import path
        msg = (
            "list_audio_devices requires optional dependency "
            "'sounddevice'. Install: pip install -e \".[audio]\""
        )
        raise ImportError(msg) from exc

    devices: list[AudioDeviceInfo] = []
    for i, raw in enumerate(sd.query_devices()):
        devices.append(
            AudioDeviceInfo(
                index=i,
                name=str(raw["name"]),
                max_input_channels=int(raw["max_input_channels"]),
                max_output_channels=int(raw["max_output_channels"]),
                default_samplerate=_as_float_or_none(raw.get("default_samplerate")),
            )
        )
    return devices


def _as_float_or_none(value: object) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return float(value)
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return None
    return None
