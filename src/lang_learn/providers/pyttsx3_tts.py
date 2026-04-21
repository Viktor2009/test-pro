"""TTS через pyttsx3 (Windows SAPI / espeak на Linux): выход WAV."""

from __future__ import annotations

import os
import tempfile
from typing import Any

from lang_learn.audio_io.wav_utils import read_wav_int16_mono, wav_duration_ms
from lang_learn.contracts.tts import TTSProvider
from lang_learn.schemas.audio import AudioFormat, TTSRequest, TTSResult


class Pyttsx3TTSProvider(TTSProvider):
    """
    Синтез речи во временный WAV и возврат байтов.

    Один экземпляр рассчитан на использование из одного потока.
    """

    def __init__(self) -> None:
        try:
            import pyttsx3 as pyttsx3_mod
        except ImportError as exc:
            msg = (
                "Pyttsx3TTSProvider requires optional dependency 'pyttsx3'. "
                'Install: pip install -e ".[audio]"'
            )
            raise ImportError(msg) from exc
        self._engine: Any = pyttsx3_mod.init()

    def synthesize(self, request: TTSRequest) -> TTSResult:
        """Сохранить речь во временный WAV и вернуть ``TTSResult``."""
        if request.audio_format not in (AudioFormat.WAV, AudioFormat.PCM):
            msg = "Pyttsx3TTSProvider supports WAV/PCM requests only"
            raise ValueError(msg)

        engine = self._engine
        if request.voice_id:
            self._apply_voice(engine, request.voice_id)
        else:
            self._apply_language_hint(engine, request.language)
        self._apply_rate(engine, request.speed)

        tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        tmp_path = tmp.name
        tmp.close()
        try:
            engine.save_to_file(request.text, tmp_path)
            engine.runAndWait()
            with open(tmp_path, "rb") as wf:
                data = wf.read()
        finally:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass

        duration_ms = wav_duration_ms(data) if data else 0
        sample_rate_hz: int | None = None
        if data:
            _, sample_rate_hz = read_wav_int16_mono(data)

        return TTSResult(
            audio=data,
            format=AudioFormat.WAV,
            sample_rate_hz=sample_rate_hz,
            duration_ms=duration_ms,
        )

    def _apply_voice(self, engine: Any, voice_id: str) -> None:
        needle = voice_id.lower()
        voices = engine.getProperty("voices")
        for voice in voices:
            vid = (getattr(voice, "id", None) or "").lower()
            name = (getattr(voice, "name", None) or "").lower()
            if needle in vid or needle in name:
                engine.setProperty("voice", voice.id)
                return

    def _apply_rate(self, engine: Any, speed: float) -> None:
        try:
            base = int(engine.getProperty("rate"))
        except (TypeError, ValueError):
            base = 200
        if base <= 0:
            base = 200
        engine.setProperty(
            "rate",
            max(50, min(400, int(base * speed))),
        )

    def _apply_language_hint(self, engine: Any, language: str) -> None:
        """Подбор голоса по BCP-47, если ``voice_id`` не задан."""
        primary = language.strip().split("-", 1)[0].lower()
        if len(primary) < 2:
            return
        voices = engine.getProperty("voices")
        for voice in voices:
            langs = getattr(voice, "languages", None) or []
            for raw in langs:
                label = self._normalize_lang_label(raw)
                if label.startswith(primary):
                    engine.setProperty("voice", voice.id)
                    return

    @staticmethod
    def _normalize_lang_label(raw: object) -> str:
        if isinstance(raw, bytes):
            return raw.decode("utf-8", errors="ignore").lower()
        return str(raw).lower()
