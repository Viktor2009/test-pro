"""
Панель вкладки «Урок 1: алфавит»: упражнения Pre-A0 без LLM (tkinter).

Встраивается в ``desktop_chat`` как ``PreA0AlphabetLesson``. Логика заданий —
в ``learning.pre_a0_engine``; здесь только разметка и обработчики кнопок.

Параметры для ручной подстройки (в ``__init__``):
  - ``voice_language_cb`` — опционально ``() -> str`` (BCP-47) для STT;
  - ``padding`` у ``Frame`` / ``LabelFrame`` — отступы вокруг блоков;
  - ``pady`` / ``padx`` в ``pack`` / ``grid`` — зазоры между секциями;
  - ``height`` у ``ScrolledText`` («Задание», «Результат») — число строк;
  - ``width`` у ``Combobox`` — условная ширина списка упражнений;
  - ``wraplength`` у ``Label`` с вариантами букв — перенос длинной строки (пиксели).

Стиль цветов и шрифтов задаётся в ``theme.py``; к полям текста применяется
``style_text_widget`` из палитры главного окна.
"""

from __future__ import annotations

import sys
import threading
import tkinter as tk
import uuid
from tkinter import messagebox, scrolledtext, ttk
from typing import Callable, cast

from lang_learn.audio_io.pyttsx3_speak_chunks import speak_pyttsx3_chunks
from lang_learn.audio_io.recorder import MicrophoneRecorder
from lang_learn.contracts.progress import ProgressRepository
from lang_learn.contracts.stt import STTProvider
from lang_learn.gui.pre_a0_alphabet_voice_flow import pick_alphabet_voice_flow
from lang_learn.gui.theme import style_text_widget, voice_status_text_font
from lang_learn.gui.waveform_compare import WaveformCompareFrame
from lang_learn.learning import pronunciation
from lang_learn.learning.course_loader import load_packaged_en_sample
from lang_learn.learning.pre_a0_engine import (
    PreA0LessonEngine,
    short_grapheme_answer_matches,
)
from lang_learn.providers.pyttsx3_tts import Pyttsx3TTSProvider
from lang_learn.schemas.audio import AudioFormat, STTRequest, TTSRequest
from lang_learn.schemas.common import EntityId, LanguageCode
from lang_learn.schemas.learning import AttemptRecord, ExercisePayload, LessonContext
from lang_learn.schemas.pre_a0 import ExerciseKind

# Зачёт замкнутой проверки «TTS эталона → WAV → STT»: метрика max(близость, STT).
_TRACT_SELF_LOOP_PASS = 0.88


def _reference_for_ui_score(ex: ExercisePayload) -> str:
    """Эталон для оценки близости (как в движке Pre-A0)."""
    if ex.kind == ExerciseKind.RECOGNIZE_LETTER.value:
        return str(ex.metadata.get("correct", ex.reference_text or ""))
    return ex.reference_text or ""


# Слова, которые типичный en-US TTS читает как *название* буквы (/eɪ/ для A
# и т.д.), без длинных поясняющих предложений. Одиночная «A» у SAPI часто = /ə/.
_LETTER_NAME_TTS: dict[str, str] = {
    "A": "ay",
    "B": "bee",
    "C": "see",
    "D": "dee",
    "E": "ee",
    "F": "eff",
    "G": "jee",
    "H": "aitch",
    "I": "eye",
    "J": "jay",
    "K": "kay",
    "L": "ell",
    "M": "em",
    "N": "en",
    "O": "oh",
    "P": "pee",
    "Q": "cue",
    "R": "are",
    "S": "ess",
    "T": "tee",
    "U": "you",
    "V": "vee",
    "W": "double you",
    "X": "ex",
    "Y": "why",
    "Z": "zee",
}


def _letter_name_tts_token(grapheme: str) -> str | None:
    g = (grapheme or "").strip().upper()
    if len(g) != 1:
        return None
    return _LETTER_NAME_TTS.get(g)


def english_tts_chunks(ex: ExercisePayload) -> list[str]:
    """
    Короткие фрагменты для pyttsx3 по очереди (без целых пояснительных фраз).

    Для буквы «слушай»: сначала звук названия (например «ay» для A), затем
    опорное слово («apple»). Для «A apple» одной строкой SAPI даёт артикль.
    """
    ref = (ex.reference_text or "").strip()
    if not ref:
        return []

    if ex.kind == ExerciseKind.LISTEN_REPEAT.value:
        if ex.metadata.get("letter_id"):
            parts = ref.split(None, 1)
            if len(parts) >= 2:
                letter, word = parts[0], parts[1]
                token = _letter_name_tts_token(letter)
                if token:
                    return [token, word]
                return [letter, word]
            if len(parts) == 1:
                tok = _letter_name_tts_token(parts[0])
                if tok:
                    return [tok]
                return [parts[0]]
        if ex.metadata.get("cluster_id"):
            parts = ref.split(None, 1)
            if len(parts) >= 2:
                return [parts[0], parts[1]]
            return [ref]
        if ex.metadata.get("pair_id"):
            return [ref]

    if ex.kind == ExerciseKind.READ_ALOUD_COMPARE.value:
        if ex.metadata.get("letter_id") and len(ref) == 1:
            tok = _letter_name_tts_token(ref)
            if tok:
                return [tok]
        if ex.metadata.get("cluster_id"):
            return [ref]

    if ex.kind == ExerciseKind.RECOGNIZE_LETTER.value:
        letter = str(ex.metadata.get("correct", ref))
        if len(letter) == 1:
            tok = _letter_name_tts_token(letter)
            if tok:
                return [tok]

    if len(ref) == 1 and ref.isascii() and ref.isalpha():
        tok = _letter_name_tts_token(ref)
        if tok:
            return [tok]

    return [ref]


class PreA0AlphabetLesson(ttk.Frame):
    """
    Линейный урок: слушай–повтори, прочитай, выбери букву; затем кластеры и пара.

    Вертикальный порядок блоков: заголовок → отладочный переход к упражнению →
    задание → варианты (при необходимости) → озвучка → ответ → проверка → результат.
    """

    def __init__(
        self,
        master: tk.Misc,
        *,
        user_id: EntityId,
        repo: ProgressRepository,
        on_attempt_saved: Callable[[], None],
        voice_language_cb: Callable[[], str] | None = None,
    ) -> None:
        # padding: внутренний отступ карточки урока на вкладке (гориз., верт.).
        super().__init__(master, style="Card.TFrame", padding=(1, 1))
        self._user_id = user_id
        self._repo = repo
        self._on_attempt_saved = on_attempt_saved
        self._voice_language_cb = voice_language_cb
        self._engine = PreA0LessonEngine(load_packaged_en_sample())
        self._ctx = LessonContext(user_id=user_id)
        self._current: ExercisePayload | None = None
        self._check_busy = False
        self._playback_id = 0
        self._silence_after_id: str | None = None
        self._tts_lock = threading.Lock()
        self._voice_busy = False
        self._stt: STTProvider | None = None
        self._stt_resolve_failed = False
        self._tract_busy = False

        title = ttk.Label(
            self,
            text="Урок 1: английский алфавит",
            style="Title.TLabel",
        )
        title.pack(anchor=tk.W, pady=(0, 0))

        dbg = ttk.LabelFrame(
            self,
            text="Переход к упражнению",
            style="OnCard.TLabelframe",
            padding=(1, 1),
        )
        # pady=(сверху, снизу): отступ рамки «Переход к упражнению» от соседних блоков.
        dbg.pack(fill=tk.X, pady=(1, 0))
        entries = self._engine.exercise_menu_entries()
        self._debug_exercise_ids: list[str] = [e[0] for e in entries]
        self._debug_combo_vals: list[str] = [
            f"{i + 1}. {lab}" for i, (_, lab) in enumerate(entries)
        ]
        self._debug_ex_combo = ttk.Combobox(
            dbg,
            values=self._debug_combo_vals,
            state="readonly",
            # Условная ширина выпадающего списка в символах.
            width=62,
        )
        if self._debug_combo_vals:
            self._debug_ex_combo.set(self._debug_combo_vals[0])
        self._debug_ex_combo.grid(row=0, column=0, sticky=tk.EW, padx=(0, 4))
        ttk.Button(
            dbg,
            text="Перейти",
            style="Muted.TButton",
            command=self._on_debug_seek,
        ).grid(row=0, column=1, sticky=tk.E)
        dbg.columnconfigure(0, weight=1)

        inst_fr = ttk.LabelFrame(
            self,
            text="Задание",
            style="LessonTask.TLabelframe",
            padding=(1, 1),
        )
        inst_fr.pack(fill=tk.BOTH, expand=False)
        self._instructions = scrolledtext.ScrolledText(
            inst_fr,
            # Минимальная высота текста задания в строках.
            height=3,
            wrap=tk.WORD,
            state=tk.DISABLED,
        )
        self._instructions.pack(fill=tk.BOTH, expand=True, pady=(0, 0))

        opt_fr = ttk.Frame(self, style="OnCard.TFrame")
        opt_fr.pack(fill=tk.X, pady=(1, 0))
        self._options_lbl = ttk.Label(
            opt_fr,
            text="",
            # Макс. ширина строки в пикселях до переноса (зависит от шрифта).
            wraplength=640,
            style="OnCard.TLabel",
        )
        self._options_lbl.pack(anchor=tk.W)

        btn_fr = ttk.Frame(self, style="OnCard.TFrame")
        btn_fr.pack(fill=tk.X, pady=(2, 0))
        self._speak_ref_btn = ttk.Button(
            btn_fr,
            text="Озвучить эталон",
            style="Muted.TButton",
            command=self._on_listen,
        )
        self._speak_ref_btn.pack(side=tk.LEFT)
        self._tract_btn = ttk.Button(
            btn_fr,
            text="Проверка тракта",
            style="Muted.TButton",
            command=self._on_tract_calibration,
        )
        self._tract_btn.pack(side=tk.LEFT, padx=(8, 0))
        self._voice_status = ttk.Label(
            btn_fr,
            text="",
            style="VoiceStatus.TLabel",
        )
        self._voice_status.pack(side=tk.LEFT, padx=(12, 0))

        wave_fr = ttk.LabelFrame(
            self,
            text="Сравнение звука: эталон и ваша запись",
            style="OnCard.TLabelframe",
            padding=(1, 1),
        )
        wave_fr.pack(fill=tk.BOTH, expand=False, pady=(2, 0))
        top_early = self.winfo_toplevel()
        pal_early = getattr(top_early, "_lang_learn_palette", None)
        self._wave_compare = WaveformCompareFrame(
            wave_fr,
            height_px=400,
            palette=pal_early if isinstance(pal_early, dict) else None,
        )
        self._wave_compare.pack(fill=tk.BOTH, expand=True)

        ans_fr = ttk.LabelFrame(
            self,
            text="Ваш ответ",
            style="OnCard.TLabelframe",
            padding=(1, 1),
        )
        ans_fr.pack(fill=tk.X, pady=(2, 0))
        self._entry = ttk.Entry(ans_fr)
        self._entry.pack(fill=tk.X, expand=True)
        self._entry.bind("<Return>", self._on_entry_return)

        act_fr = ttk.Frame(self, style="OnCard.TFrame")
        act_fr.pack(fill=tk.X, pady=(2, 0))
        ttk.Button(
            act_fr,
            text="Проверить",
            style="Muted.TButton",
            command=self._on_check,
        ).pack(side=tk.LEFT)

        fb_fr = ttk.LabelFrame(
            self,
            text="",
            style="OnCard.TLabelframe",
            padding=(1, 1),
        )
        # expand=True: блок «Результат» забирает оставшуюся высоту вкладки.
        fb_fr.pack(fill=tk.BOTH, expand=True, pady=(2, 0))
        self._feedback = scrolledtext.ScrolledText(
            fb_fr,
            # Минимальная высота области обратной связи в строках.
            height=3,
            wrap=tk.WORD,
            state=tk.DISABLED,
        )
        self._feedback.pack(fill=tk.BOTH, expand=True, pady=(0, 0))

        top = self.winfo_toplevel()
        pal = getattr(top, "_lang_learn_palette", None)
        if isinstance(pal, dict):
            style_text_widget(
                self._instructions,
                pal,
                font=voice_status_text_font(),
            )
            style_text_widget(
                self._feedback,
                pal,
                font=voice_status_text_font(),
            )

        self.bind("<Destroy>", self._on_destroy, add="+")

        self._load_next_exercise()
        # При запуске приложения фокусируем «Озвучить эталон».
        self._tk_main().after_idle(self._speak_ref_btn.focus_set)

    def _on_destroy(self, _event: tk.Event) -> None:
        self._cancel_silence_timer()

    def _tk_main(self) -> tk.Misc:
        """Окно для ``after`` / ``after_cancel`` (поток главного цикла tk)."""
        return self.winfo_toplevel()

    def _target_language(self) -> LanguageCode:
        if self._voice_language_cb is not None:
            raw = (self._voice_language_cb() or "").strip()
            if raw:
                return cast(LanguageCode, raw)
        return cast(LanguageCode, "en-US")

    def _cancel_silence_timer(self) -> None:
        sid = self._silence_after_id
        if sid is not None:
            try:
                self._tk_main().after_cancel(sid)
            except tk.TclError:
                pass
            self._silence_after_id = None

    def _set_voice_status(self, text: str) -> None:
        self._voice_status.configure(text=text)

    def _resolve_stt(self) -> STTProvider | None:
        if self._stt_resolve_failed:
            return None
        if self._stt is not None:
            return self._stt
        try:
            from lang_learn.plugins.bootstrap import create_default_registry

            reg = create_default_registry(with_audio_extras=True)
            self._stt = reg.create_stt("faster_whisper")
        except Exception as exc:
            self._stt_resolve_failed = True
            self._stt = None
            self._append_feedback(
                "Распознавание речи (faster-whisper) недоступно: "
                f"{type(exc).__name__}: {exc}. Для голосового ответа установите "
                'зависимости: pip install -e ".[audio]"',
            )
        return self._stt

    def _on_debug_seek(self) -> None:
        if self._voice_busy or self._check_busy or self._tract_busy:
            messagebox.showinfo(
                "Переход",
                "Дождитесь окончания записи/проверки/проверки тракта.",
            )
            return
        cur = self._debug_ex_combo.current()
        if cur < 0 or cur >= len(self._debug_exercise_ids):
            messagebox.showinfo(
                "Переход",
                "Выберите строку в списке упражнений.",
            )
            return
        eid = self._debug_exercise_ids[cur]
        if not self._engine.seek_user_to_exercise(str(self._user_id), eid):
            messagebox.showwarning(
                "Переход",
                f"Не удалось перейти к «{eid}».",
            )
            return
        self._append_feedback(f"Переход: загружается упражнение «{eid}»…")
        self._tk_main().after_idle(self._load_next_exercise)

    def _set_instructions(self, text: str) -> None:
        self._instructions.configure(state=tk.NORMAL)
        self._instructions.delete("1.0", tk.END)
        self._instructions.insert("1.0", text)
        self._instructions.configure(state=tk.DISABLED)

    def _append_feedback(self, text: str) -> None:
        self._feedback.configure(state=tk.NORMAL)
        self._feedback.insert(tk.END, text + "\n\n")
        self._feedback.see(tk.END)
        self._feedback.configure(state=tk.DISABLED)

    def _clear_feedback(self) -> None:
        self._feedback.configure(state=tk.NORMAL)
        self._feedback.delete("1.0", tk.END)
        self._feedback.configure(state=tk.DISABLED)

    def _load_next_exercise(self) -> None:
        self._cancel_silence_timer()
        self._playback_id += 1
        self._set_voice_status("")
        self._wave_compare.clear()

        ex = self._engine.next_exercise(self._ctx)
        self._current = ex
        self._entry.delete(0, tk.END)
        self._clear_feedback()

        self._set_instructions(ex.instructions)

        opts = ex.metadata.get("options")
        if (
            ex.kind == ExerciseKind.RECOGNIZE_LETTER.value
            and isinstance(opts, list)
            and opts
        ):
            flat = ", ".join(str(x) for x in opts)
            self._options_lbl.configure(text=f"Варианты букв: {flat}")
        else:
            self._options_lbl.configure(text="")

        self._sync_debug_combo_to_current()

    def _sync_debug_combo_to_current(self) -> None:
        ex = self._current
        if ex is None or not self._debug_exercise_ids:
            return
        eid = str(ex.exercise_id)
        if eid not in self._debug_exercise_ids:
            return
        idx = self._debug_exercise_ids.index(eid)
        if 0 <= idx < len(self._debug_combo_vals):
            self._debug_ex_combo.current(idx)
            self._debug_ex_combo.set(self._debug_combo_vals[idx])

    def _on_entry_return(self, _event: tk.Event) -> str:
        """Один вызов проверки и без всплытия (иначе Enter может сработать дважды)."""
        self._on_check()
        return "break"

    def _synthesize_join_text_wav(
        self,
        join_text: str,
        lang: LanguageCode,
    ) -> bytes:
        """Синтез строки эталона в WAV (pyttsx3); вызывать под ``_tts_lock``."""
        coinit = False
        if sys.platform == "win32":
            try:
                import pythoncom

                pythoncom.CoInitialize()
                coinit = True
            except ImportError:
                pass
        try:
            tts = Pyttsx3TTSProvider()
            tres = tts.synthesize(
                TTSRequest(
                    text=join_text,
                    language=lang,
                    audio_format=AudioFormat.WAV,
                ),
            )
            return tres.audio
        finally:
            if coinit:
                try:
                    import pythoncom

                    pythoncom.CoUninitialize()
                except ImportError:
                    pass

    def _speak_reference(self, playback_id: int) -> None:
        ex = self._current
        if ex is None:
            return
        chunks = english_tts_chunks(ex)
        if not chunks:
            messagebox.showinfo("Озвучка", "Для этого шага нет текста эталона.")
            return

        # Снимок корня только из потока UI (tk не потокобезопасен).
        root = self.winfo_toplevel()
        lang = self._target_language()

        def work() -> None:
            err: str | None
            wav_ref: bytes | None = None
            with self._tts_lock:
                err = speak_pyttsx3_chunks(chunks)
                if err is None:
                    jt = " ".join(chunks).strip()
                    if jt:
                        try:
                            wav_ref = self._synthesize_join_text_wav(jt, lang)
                        except (ImportError, OSError, RuntimeError, ValueError):
                            wav_ref = None
            if err is not None:

                def _show_tts_problem() -> None:
                    if playback_id != self._playback_id:
                        return
                    messagebox.showwarning("Озвучка", err)

                root.after(0, _show_tts_problem)
                return

            pb_done = playback_id

            def _after_listen_ui() -> None:
                if playback_id != self._playback_id:
                    return
                if wav_ref:
                    self._wave_compare.set_reference_wav(wav_ref)
                self._after_reference_playback(pb_done)

            root.after(0, _after_listen_ui)

        threading.Thread(target=work, daemon=True).start()

    def _after_reference_playback(self, playback_id: int) -> None:
        if playback_id != self._playback_id:
            return
        ex = self._current
        if ex is None:
            return
        flow = pick_alphabet_voice_flow(ex)
        if flow is None:
            self._set_voice_status("")
            return
        stt = self._resolve_stt()
        if stt is None:
            if self._stt_resolve_failed:
                self._set_voice_status(
                    "Голосовой ответ недоступен (нет STT). "
                    "Введите ответ вручную.",
                )
            else:
                self._set_voice_status("")
            return
        timing = flow.timing(ex)
        delay_ms = max(200, int(round(timing.silence_after_reference_s * 1000)))
        self._cancel_silence_timer()
        self._set_voice_status(
            f"Через {timing.silence_after_reference_s:.1f} с — запись "
            f"({timing.record_duration_s:.0f} с)…",
        )
        ex_id = str(ex.exercise_id)

        def fire() -> None:
            self._silence_after_id = None
            self._on_silence_elapsed(playback_id, ex_id, timing.record_duration_s)

        self._silence_after_id = self._tk_main().after(delay_ms, fire)

    def _on_silence_elapsed(
        self,
        playback_id: int,
        exercise_id: str,
        record_duration_s: float,
    ) -> None:
        if playback_id != self._playback_id:
            return
        ex = self._current
        if ex is None or str(ex.exercise_id) != exercise_id:
            return
        if pick_alphabet_voice_flow(ex) is None:
            return
        if self._voice_busy or self._check_busy:
            self._append_feedback(
                "Запись пропущена: дождитесь окончания проверки или предыдущей "
                "записи.",
            )
            return
        stt = self._resolve_stt()
        if stt is None:
            self._append_feedback(
                "Запись не запущена: нет рабочего STT. См. сообщение выше "
                "или установите зависимости [audio].",
            )
            return
        self._begin_voice_capture(record_duration_s, stt)

    def _begin_voice_capture(self, duration_s: float, stt: STTProvider) -> None:
        if self._voice_busy:
            return
        self._voice_busy = True
        self._set_voice_status("Слушаю микрофон…")
        self._append_feedback(
            f"Запись с микрофона ({duration_s:.0f} с), затем распознавание…",
        )
        root = self.winfo_toplevel()
        cap_id = self._playback_id
        lang = self._target_language()

        def work() -> None:
            err: str | None = None
            text = ""
            wav: bytes | None = None
            try:
                rec = MicrophoneRecorder()
                wav = rec.record_seconds(duration_s)
                result = stt.transcribe(
                    STTRequest(audio=wav, language=lang),
                )
                text = (result.text or "").strip()
            except ImportError as exc:
                err = str(exc)
            except (OSError, RuntimeError, ValueError) as exc:
                err = str(exc)
            except Exception as exc:
                err = f"{type(exc).__name__}: {exc}"

            captured = wav

            def done() -> None:
                self._voice_busy = False
                if cap_id != self._playback_id:
                    self._set_voice_status("")
                    return
                if captured is not None:
                    self._wave_compare.set_user_wav(captured)
                if err is not None:
                    self._set_voice_status("")
                    self._append_feedback(f"Запись/распознавание: {err}")
                    messagebox.showwarning(
                        "Микрофон / распознавание",
                        err[:400] + ("…" if len(err) > 400 else ""),
                    )
                    return
                if not text:
                    self._set_voice_status("")
                    self._append_feedback(
                        "Речь не распознана. Повторите эталон и снова дождитесь "
                        "записи или введите ответ вручную.",
                    )
                    return
                self._entry.delete(0, tk.END)
                self._entry.insert(0, text)
                self._set_voice_status("Проверка ответа…")
                self._on_check()
                self._set_voice_status("")

            root.after(0, done)

        threading.Thread(target=work, daemon=True).start()

    def _finish_tract_ui(self) -> None:
        """Снять блокировку кнопки эталонной проверки тракта (только из потока UI)."""
        self._tract_busy = False
        try:
            self._tract_btn.state(["!disabled"])
        except tk.TclError:
            pass

    def _on_tract_calibration(self) -> None:
        """
        Замкнутая проверка эталона: тот же текст → синтез в WAV → STT по этому
        WAV → сравнение с эталоном (без микрофона и без воспроизведения в динамики).
        """
        if self._tract_busy:
            return
        if self._voice_busy or self._check_busy:
            messagebox.showinfo(
                "Проверка тракта",
                "Дождитесь окончания записи, проверки ответа или другой операции.",
            )
            return
        ex = self._current
        if ex is None:
            return
        chunks = english_tts_chunks(ex)
        if not chunks:
            messagebox.showinfo(
                "Проверка тракта",
                "Для этого шага нет эталона озвучки.",
            )
            return
        join_text = " ".join(chunks).strip()
        if not join_text:
            messagebox.showinfo(
                "Проверка тракта",
                "Пустой текст для синтеза эталона.",
            )
            return
        stt = self._resolve_stt()
        if stt is None:
            messagebox.showwarning(
                "Проверка тракта",
                "Нужен STT (faster-whisper). Установите: pip install -e \".[audio]\"",
            )
            return

        self._cancel_silence_timer()
        self._playback_id += 1
        self._tract_busy = True
        self._tract_btn.state(["disabled"])
        self._set_voice_status("Проверка тракта…")
        self._append_feedback("Тракт: запуск замкнутой проверки…")

        root = self.winfo_toplevel()
        lang = self._target_language()
        ref_text = _reference_for_ui_score(ex)
        ex_id = str(ex.exercise_id)

        def work() -> None:
            def ui(fn: Callable[[], None]) -> None:
                root.after(0, fn)

            def log(msg: str) -> None:
                def _append() -> None:
                    self._append_feedback(msg)

                ui(_append)

            try:
                log(
                    "▶ Эталон на самого себя: синтез тех же фрагментов в один WAV "
                    "(как для урока), затем распознавание этого WAV тем же STT и "
                    "сравнение с текстом эталона. Микрофон не используется.",
                )
                log(f"▶ Строка синтеза: «{join_text}» (эталон урока: «{ref_text}»).")

                with self._tts_lock:
                    wav = self._synthesize_join_text_wav(join_text, lang)
                root.after(0, lambda w=wav: self._wave_compare.set_reference_wav(w))

                log(
                    f"▶ WAV готов ({len(wav)} байт). Распознавание (STT, без VAD)…",
                )
                prompt = join_text[:448] if join_text else None
                req = STTRequest(
                    audio=wav,
                    language=lang,
                    vad_filter=False,
                    initial_prompt=prompt,
                )
                result = stt.transcribe(req)
                transcribed = (result.text or "").strip()
                if not transcribed:
                    log("▶ Повтор STT с авто-определением языка…")
                    result = stt.transcribe(
                        STTRequest(
                            audio=wav,
                            language=None,
                            vad_filter=False,
                            initial_prompt=prompt,
                        ),
                    )
                    transcribed = (result.text or "").strip()

                ex_after = self._current

                def finish() -> None:
                    self._finish_tract_ui()
                    self._set_voice_status("")
                    if ex_after is None or str(ex_after.exercise_id) != ex_id:
                        self._append_feedback(
                            "Тракт: упражнение сменили — итог не применён.",
                        )
                        return
                    if not transcribed:
                        self._append_feedback(
                            "▶ Итог: пустой распознанный текст по синтезированному "
                            "эталону. Проверьте faster-whisper и язык сессии.",
                        )
                        return
                    sim_ref = pronunciation.utterance_similarity(
                        ref_text,
                        transcribed,
                    )
                    sim_join = pronunciation.utterance_similarity(
                        join_text,
                        transcribed,
                    )
                    sim = max(sim_ref, sim_join)
                    stt_conf = (
                        float(result.confidence)
                        if result.confidence is not None
                        else 0.0
                    )
                    tract_metric = max(sim, stt_conf)
                    passed = tract_metric >= _TRACT_SELF_LOOP_PASS
                    self._append_feedback(
                        f"▶ Сравнение с эталоном урока «{ref_text}» и строкой "
                        f"синтеза «{join_text}».\n"
                        f"Распознано: «{transcribed}». Близость к эталону: "
                        f"{sim_ref:.2f}, к строке синтеза: {sim_join:.2f} "
                        f"(max {sim:.2f}). Уверенность STT: {stt_conf:.2f}. "
                        f"Метрика max(близость, STT): {tract_metric:.2f}.",
                    )
                    if short_grapheme_answer_matches(ex_after, transcribed):
                        self._append_feedback(
                            "Тракт: по ключевой графеме совпадает с эталоном.",
                        )
                    if passed:
                        self._append_feedback(
                            f"Тракт: зачёт замкнутого контура "
                            f"(≥ {_TRACT_SELF_LOOP_PASS:.0%}).",
                        )
                        # Исторически кнопка «Проверка тракта» должна давать зачёт 1.0.
                        # Сохраняем отдельную попытку, чтобы она попадала в «Сравнение
                        # и рекомендации» и KPI/прогресс.
                        aid = f"tract-{uuid.uuid4().hex[:16]}"
                        self._repo.save_attempt(
                            AttemptRecord(
                                attempt_id=aid,
                                user_id=self._user_id,
                                exercise_id=ex_after.exercise_id,
                                transcript=transcribed,
                                score=1.0,
                                details={
                                    "skill_axis": "pronunciation",
                                    "lesson": "pre_a0_alphabet_1",
                                    "kind": ex_after.kind,
                                    "accepted": True,
                                    "reference_text": ref_text,
                                    "recommendation_next": (
                                        "Тракт пройден (замкнутый контур ≥ порога)."
                                    ),
                                    "tract_metric": tract_metric,
                                    "stt_confidence": stt_conf,
                                    "sim_ref": sim_ref,
                                    "sim_join": sim_join,
                                },
                            ),
                        )
                        self._on_attempt_saved()
                    else:
                        self._append_feedback(
                            f"Тракт: ниже порога замкнутого контура "
                            f"({_TRACT_SELF_LOOP_PASS:.0%}) — модель STT может "
                            "иначе интерпретировать синтезированную речь.",
                        )

                ui(finish)
            except ImportError as exc:
                imp_txt = str(exc)

                def imp_err() -> None:
                    self._append_feedback(f"Тракт: {imp_txt}")
                    self._finish_tract_ui()
                    self._set_voice_status("")

                ui(imp_err)
            except (OSError, RuntimeError, ValueError) as exc:
                io_txt = str(exc)

                def io_err() -> None:
                    self._append_feedback(f"Тракт: ошибка — {io_txt}")
                    messagebox.showwarning(
                        "Проверка тракта",
                        io_txt[:500] + ("…" if len(io_txt) > 500 else ""),
                    )
                    self._finish_tract_ui()
                    self._set_voice_status("")

                ui(io_err)
            except Exception as exc:
                gen_name = type(exc).__name__
                gen_txt = str(exc)

                def gen_err() -> None:
                    self._append_feedback(
                        f"Тракт: неожиданная ошибка — {gen_name}: {gen_txt}",
                    )
                    messagebox.showwarning(
                        "Проверка тракта",
                        f"{gen_name}: {gen_txt}"[:500]
                        + ("…" if len(gen_txt) > 500 else ""),
                    )
                    self._finish_tract_ui()
                    self._set_voice_status("")

                ui(gen_err)

        threading.Thread(target=work, daemon=True).start()

    def _on_listen(self) -> None:
        self._cancel_silence_timer()
        ex = self._current
        if ex is None:
            return
        if not english_tts_chunks(ex):
            messagebox.showinfo(
                "Озвучка",
                "Для этого шага нет текста эталона.",
            )
            return
        self._playback_id += 1
        pb = self._playback_id
        self._speak_reference(pb)

    def _on_check(self) -> None:
        if self._check_busy:
            return
        self._check_busy = True
        try:
            ex = self._current
            if ex is None:
                return
            raw = self._entry.get().strip()
            if not raw:
                # Если текст не введён, пробуем голосовой ввод (если доступен STT).
                stt = self._resolve_stt()
                if stt is None:
                    messagebox.showwarning(
                        "Пустой ввод",
                        "Сначала введите ответ, затем «Проверить» или Enter.",
                    )
                    return
                flow = pick_alphabet_voice_flow(ex)
                duration_s = flow.timing(ex).record_duration_s if flow else 4.0
                self._append_feedback(
                    "Пустой ввод: запускаю запись с микрофона для распознавания…",
                )
                # Важно: снимаем флаг, потому что запись завершается колбэком,
                # который снова вызовет _on_check().
                self._check_busy = False
                self._begin_voice_capture(duration_s, stt)
                return

            aid = f"prea0-{uuid.uuid4().hex[:16]}"
            attempt = AttemptRecord(
                attempt_id=aid,
                user_id=self._user_id,
                exercise_id=ex.exercise_id,
                transcript=raw,
            )
            fb = self._engine.submit_attempt(attempt)
            ref = _reference_for_ui_score(ex)
            base_score = (
                pronunciation.utterance_similarity(ref, raw) if ref or raw else 0.0
            )
            # В UI оценка должна отражать зачёт: если попытка принята движком,
            # сохраняем 1.0. Иначе по "похожести" одна буква против фразы
            # часто даёт ~0.5.
            score = 1.0 if fb.accepted else base_score

            self._repo.save_attempt(
                AttemptRecord(
                    attempt_id=aid,
                    user_id=self._user_id,
                    exercise_id=ex.exercise_id,
                    transcript=raw,
                    score=score,
                    details={
                        "skill_axis": "pronunciation",
                        "lesson": "pre_a0_alphabet_1",
                        "kind": ex.kind,
                        "accepted": fb.accepted,
                    },
                ),
            )
            self._on_attempt_saved()

            line = fb.summary
            if fb.next_hint:
                line += f"\nПодсказка: {fb.next_hint}"
            self._append_feedback(line)

            if fb.accepted:
                self._append_feedback("Верно. Загружается следующее упражнение…")
                # Планируем переход через after_idle, чтобы не блокировать обновление
                # UI (и избежать конфликтов, если проверка была запущена колбэком).
                self._tk_main().after_idle(self._load_next_exercise)
            else:
                self._append_feedback(
                    "Попробуйте ещё раз (ответ можно исправить).",
                )
        finally:
            self._check_busy = False
