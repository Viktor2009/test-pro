"""
Два графика формы сигнала: эталон (синтез) и запись пользователя (tk.Canvas).

Требует ``numpy`` и корректный WAV (extra ``[audio]``).
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Mapping

from lang_learn.audio_io.wav_envelope import wav_to_envelope_xy

# Общая ось времени (секунды) после обрезки ведущей тишины по огибающей.
# Вертикаль: эталон даёт шкалу; пик эталона (ys=1) занимает эту долю высоты
# до нулевой линии; запись масштабируется как ys * (peak_user / peak_ref).
_REF_HEADROOM = 0.84
_LINE_WIDTH = 4
_ONSET_THRESHOLD = 0.08
# Запись часто до ~5 с; для сравнения с коротким эталоном показываем не более:
_USER_WAV_MAX_DISPLAY_S = 2.5
# Горизонтальная шкала (фиксированная): 2.0 секунды.
_X_AXIS_S = 2.0
# Ноль огибающей: y = 95% высоты (область ≥0 вверх).
_BASELINE_Y_FRACTION = 0.95
_BASELINE_LINE_WIDTH = 1
_MARGIN_H = 5
_MARGIN_V = 4


class WaveformCompareFrame(ttk.Frame):
    """Вертикально: эталон, затем запись пользователя."""

    def __init__(
        self,
        master: tk.Misc,
        *,
        height_px: int = 200,
        palette: Mapping[str, str] | None = None,
    ) -> None:
        super().__init__(master, style="OnCard.TFrame")
        self._height_px = height_px
        self._pal = dict(palette) if palette else {}
        self._bg = self._pal.get("text_area_bg", "#f0f7fb")
        self._ref_color = "#1565c0"
        self._user_color = "#c62828"
        self._fg_muted = self._pal.get("fg_muted", "#505050")
        self._baseline_fg = self._pal.get("wave_zero_line", "#9eb0c0")

        self._ref_wav: bytes | None = None
        self._user_wav: bytes | None = None

        half = max(120, (height_px - 36) // 2)
        self._lbl_ref = ttk.Label(self, text="Эталон (синтез)", style="OnCard.TLabel")
        self._lbl_ref.pack(anchor=tk.W)
        self._cv_ref = tk.Canvas(
            self,
            height=half,
            highlightthickness=0,
            bg=self._bg,
        )
        self._cv_ref.pack(fill=tk.BOTH, expand=True)
        self._lbl_user = ttk.Label(self, text="Ваша запись", style="OnCard.TLabel")
        self._lbl_user.pack(anchor=tk.W, pady=(4, 0))
        self._cv_user = tk.Canvas(
            self,
            height=half,
            highlightthickness=0,
            bg=self._bg,
        )
        self._cv_user.pack(fill=tk.BOTH, expand=True)

        self._cv_ref.bind("<Configure>", self._on_configure)
        self._cv_user.bind("<Configure>", self._on_configure)

    def _on_configure(self, _event: tk.Event) -> None:
        self.after_idle(self._redraw_all)

    def clear(self) -> None:
        """Очистить данные и графики."""
        self._ref_wav = None
        self._user_wav = None
        self._redraw_all()

    def set_reference_wav(self, wav: bytes | None) -> None:
        """Обновить эталон (обычно после «Озвучить эталон»)."""
        self._ref_wav = wav
        self._redraw_all()

    def set_user_wav(self, wav: bytes | None) -> None:
        """Обновить запись пользователя (после микрофона)."""
        self._user_wav = wav
        self._redraw_all()

    @staticmethod
    def _onset_index(ys: list[float]) -> int:
        for i, v in enumerate(ys):
            if v >= _ONSET_THRESHOLD:
                return i
        return 0

    @classmethod
    def _trim_leading_silence(
        cls,
        xs: list[float],
        ys: list[float],
        dur: float,
    ) -> tuple[list[float], list[float], float]:
        """Сдвиг времени к первому заметному уровню — оба графика слева с «началом»."""
        i0 = cls._onset_index(ys)
        if i0 <= 0:
            return xs, ys, dur
        t0 = xs[i0]
        xs_t = [float(x - t0) for x in xs[i0:]]
        ys_t = ys[i0:]
        dur_t = max(0.0, dur - t0)
        return xs_t, ys_t, dur_t

    @classmethod
    def _envelope_trimmed(
        cls, wav: bytes | None
    ) -> tuple[list[float], list[float], float, float] | None:
        if not wav:
            return None
        xs, ys, dur, peak = wav_to_envelope_xy(wav)
        if not xs or not ys or dur <= 0:
            return None
        xt, yt, dtr = cls._trim_leading_silence(xs, ys, dur)
        if not xt or not yt or dtr <= 0:
            return None
        return xt, yt, dtr, peak

    @staticmethod
    def _cap_envelope_duration(
        env: tuple[list[float], list[float], float, float],
        max_seconds: float,
    ) -> tuple[list[float], list[float], float, float]:
        """Обрезать огибающую по времени (t ≤ max_seconds)."""
        xs, ys, dur, peak = env
        cap = max(1e-6, float(max_seconds))
        last = -1
        for i, t in enumerate(xs):
            if t <= cap + 1e-9:
                last = i
            else:
                break
        if last < 0:
            y0 = float(ys[0]) if ys else 0.0
            return [0.0, 1e-6], [y0, y0], min(dur, cap), peak
        xs_c = xs[: last + 1]
        ys_c = ys[: last + 1]
        dur_c = min(float(dur), cap)
        return xs_c, ys_c, max(dur_c, 1e-6), peak

    def _redraw_all(self) -> None:
        ref_e = self._envelope_trimmed(self._ref_wav)
        user_e = self._envelope_trimmed(self._user_wav)
        axis_s = max(_X_AXIS_S, 1e-3)
        if ref_e is not None:
            ref_e = self._cap_envelope_duration(ref_e, axis_s)
        if user_e is not None:
            user_cap = min(_USER_WAV_MAX_DISPLAY_S, axis_s)
            user_e = self._cap_envelope_duration(user_e, user_cap)
        peak_ref = float(ref_e[3]) if ref_e else 0.0
        peak_user = float(user_e[3]) if user_e else 0.0
        scale_base = max(peak_ref, 1e-9) if ref_e else max(peak_user, 1e-9)
        ratio_ref = peak_ref / scale_base if ref_e else 1.0
        ratio_user = peak_user / scale_base if user_e else 1.0
        self._redraw_canvas(
            self._cv_ref,
            ref_e,
            self._ref_color,
            "эталон",
            axis_s,
            ratio_ref,
        )
        self._redraw_canvas(
            self._cv_user,
            user_e,
            self._user_color,
            "запись",
            axis_s,
            ratio_user,
        )

    def _redraw_canvas(
        self,
        cv: tk.Canvas,
        env: tuple[list[float], list[float], float, float] | None,
        color: str,
        kind: str,
        shared_duration: float,
        vertical_ratio: float,
    ) -> None:
        cv.delete("all")
        w = max(2, cv.winfo_width())
        h = max(2, cv.winfo_height())
        cv.create_rectangle(0, 0, w, h, outline="", fill=self._bg)
        by = h * _BASELINE_Y_FRACTION
        cv.create_line(
            0,
            by,
            w,
            by,
            fill=self._baseline_fg,
            width=_BASELINE_LINE_WIDTH,
        )
        if env is None:
            cv.create_text(
                w // 2,
                h // 2,
                text=f"Нет данных ({kind})",
                fill=self._fg_muted,
            )
            return
        xs, ys, dur, _ = env
        if not xs or not ys or dur <= 0:
            cv.create_text(
                w // 2,
                h // 2,
                text="Не удалось разобрать WAV (numpy / [audio])",
                fill=self._fg_muted,
            )
            return
        baseline_y = by
        amp = max(4.0, baseline_y - float(_MARGIN_V))
        axis = max(shared_duration, 1e-6)
        y_top = float(_MARGIN_V)
        pts: list[float] = []
        vr = max(0.0, float(vertical_ratio))
        for i, t in enumerate(xs):
            x_pix = _MARGIN_H + (w - 2 * _MARGIN_H) * (t / axis)
            amp_y = ys[i] * vr * _REF_HEADROOM
            y_pix = baseline_y - amp_y * amp
            if y_pix < y_top:
                y_pix = y_top
            pts.extend([x_pix, y_pix])
        if len(pts) >= 4:
            cv.create_line(
                *pts,
                fill=color,
                width=_LINE_WIDTH,
                smooth=False,
            )
        cv.create_text(
            _MARGIN_H + 2,
            10,
            text=f"{dur:.2f} с · ось {axis:.2f} с",
            anchor=tk.W,
            fill=self._fg_muted,
        )
