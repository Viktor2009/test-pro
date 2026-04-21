"""STT через faster-whisper (локально, вход WAV)."""

from __future__ import annotations

import math
import os
import tempfile

from lang_learn.contracts.stt import STTProvider
from lang_learn.schemas.audio import AudioFormat, STTRequest, STTResult, STTSegment


def _bcp47_primary(code: str) -> str:
    return code.strip().split("-", 1)[0].lower()


def _segment_confidence(avg_logprob: float | None) -> float | None:
    if avg_logprob is None:
        return None
    try:
        return max(0.0, min(1.0, float(math.exp(avg_logprob))))
    except (OverflowError, ValueError):
        return None


class FasterWhisperSTTProvider(STTProvider):
    """
    Распознавание речи моделью faster-whisper.

    Первый запуск может скачать веса модели (зависит от ``model_size``).
    """

    def __init__(
        self,
        *,
        model_size: str = "tiny",
        device: str = "cpu",
        compute_type: str = "int8",
    ) -> None:
        try:
            from faster_whisper import WhisperModel
        except ImportError as exc:
            msg = (
                "FasterWhisperSTTProvider requires optional dependency "
                "'faster-whisper'. Install: pip install -e \".[audio]\""
            )
            raise ImportError(msg) from exc
        self._model = WhisperModel(model_size, device=device, compute_type=compute_type)

    def transcribe(self, request: STTRequest) -> STTResult:
        """Распознать моно WAV (PCM16)."""
        if request.audio_format != AudioFormat.WAV:
            msg = "FasterWhisperSTTProvider supports WAV only"
            raise ValueError(msg)

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(request.audio)
            path = f.name
        try:
            lang = _bcp47_primary(request.language) if request.language else None
            vad = True if request.vad_filter is None else bool(request.vad_filter)
            prompt = (request.initial_prompt or "").strip()
            if len(prompt) > 448:
                prompt = prompt[:448]
            transcribe_kw: dict[str, object] = {
                "language": lang,
                "vad_filter": vad,
            }
            if prompt:
                transcribe_kw["initial_prompt"] = prompt
            segments_gen, info = self._model.transcribe(path, **transcribe_kw)
            collected = list(segments_gen)
            full_text = "".join(s.text for s in collected).strip()
            seg_dtos: list[STTSegment] = []
            conf_values: list[float] = []
            for seg in collected:
                t = seg.text.strip()
                conf = _segment_confidence(seg.avg_logprob)
                if conf is not None:
                    conf_values.append(conf)
                seg_dtos.append(
                    STTSegment(
                        text=t,
                        start_ms=int(round(seg.start * 1000)),
                        end_ms=int(round(seg.end * 1000)),
                        confidence=conf,
                    ),
                )
            overall: float | None = None
            if conf_values:
                overall = sum(conf_values) / len(conf_values)
            elif getattr(info, "language_probability", None) is not None:
                lp = info.language_probability
                overall = float(lp) if lp is not None else None
            return STTResult(
                text=full_text,
                confidence=overall,
                segments=tuple(seg_dtos),
            )
        finally:
            try:
                os.unlink(path)
            except OSError:
                pass
