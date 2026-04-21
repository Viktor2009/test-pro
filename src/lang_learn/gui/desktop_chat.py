"""
Главное окно учебного приложения (tkinter).

Содержит: блок «Параметры сессии», вкладки (урок Pre-A0 и диалог с LLM),
панель «Прогресс» со сводкой KPI. Точка входа: ``run_learning_desktop()`` —
там задаётся общий кегль шрифта (``delta_pt``) и вызывается это окно.

Что подстраивать под себя (в основном в ``LearningDesktopApp._build_form`` и
в ``__init__`` класса):
  - ``geometry`` / ``minsize`` — стартовый и минимальный размер окна;
  - ``padding`` у ``Frame`` / ``LabelFrame`` — внешние отступы блоков;
  - ``pady`` / ``padx`` в ``grid`` / ``pack`` — вертикальные и горизонтальные
    зазоры между строками и виджетами;
  - ``height`` у ``Text`` / ``ScrolledText`` — число строк текста (минимальная
    высота области; при нехватке места появится прокрутка);
  - ``width`` у ``Entry`` / ``Combobox`` — условная ширина в символах;
  - ``columnconfigure(..., weight=...)`` — какие колонки сетки растягиваются
    при изменении ширины окна.

Формат текста сводки прогресса задаётся в ``_overview_lines`` (в т.ч. ``gap``
между колонками KPI/компетенций).

Три визуальные зоны (оттенки фона) задаются в ``theme.py`` ключами палитры
``bg_section_params`` (блок параметров), ``bg_section_content`` (вкладки урок
и диалог), ``bg_section_progress`` (панель прогресса).
"""

from __future__ import annotations

import json
import tkinter as tk
import tkinter.font as tkfont
from tkinter import messagebox, ttk
from tkinter.scrolledtext import ScrolledText
from typing import Literal, cast

from lang_learn.contracts.progress import ProgressRepository
from lang_learn.gui.history import append_turn_to_history
from lang_learn.gui.pre_a0_lesson import PreA0AlphabetLesson
from lang_learn.gui.preferences import (
    read_llm_provider_choice,
    resolve_initial_llm_provider,
    write_llm_provider_choice,
)
from lang_learn.gui.theme import apply_professional_theme, style_text_widget
from lang_learn.learning.dialog_orchestrator import DialogOrchestrator
from lang_learn.learning.progress_report import compute_progress_overview
from lang_learn.learning.trajectory_service import TrajectoryService
from lang_learn.persistence.app_paths import (
    default_progress_database_path,
    repository_schema_sql_path,
)
from lang_learn.persistence.sqlite_progress import SqliteProgressRepository
from lang_learn.plugins.bootstrap import create_default_registry
from lang_learn.schemas.common import LanguageCode
from lang_learn.schemas.dialog import DialogSessionContext
from lang_learn.schemas.learning import AttemptRecord, LearningProfile
from lang_learn.schemas.llm import ChatMessage, LLMProviderConfig

# Совпадает с ``EntityId``: 1…128 символов после нормализации.
_DEFAULT_GUI_USER_ID = "gui-user"


def normalize_session_user_id(raw: str) -> str:
    """
    Привести ввод к допустимому внешнему идентификатору пользователя для БД.

    Пустая строка → ``gui-user``; длина обрезается до 128 символов.
    """
    s = (raw or "").strip()
    if not s:
        return _DEFAULT_GUI_USER_ID
    if len(s) > 128:
        return s[:128]
    return s


def open_gui_sqlite_progress_repository() -> SqliteProgressRepository:
    """
    SQLite-репозиторий для GUI: схема из репозитория, файл в каталоге данных ОС.

    Raises:
        FileNotFoundError: нет ``db/schema.sql`` (неверная установка/сборка).
        OSError: не удалось создать каталог или открыть файл БД.
    """
    schema_path = repository_schema_sql_path()
    if not schema_path.is_file():
        msg = f"Не найден файл схемы БД: {schema_path}"
        raise FileNotFoundError(msg)
    db_path = default_progress_database_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return SqliteProgressRepository(db_path, schema_path=schema_path)


def _overview_lines(overview_json: str) -> str:
    """Краткое текстовое представление JSON сводки прогресса."""
    data = json.loads(overview_json)
    kpis = data.get("kpis", {})
    tr = data.get("travel", {})
    comp = data.get("competency", {})
    lx = float(comp.get("lexicon", 0))
    cm = float(comp.get("comprehension", 0))
    pr = float(comp.get("pronunciation", 0))
    dg = float(comp.get("dialog_scenario", 0))
    k1 = f"  completion_rate={kpis.get('completion_rate', 0):.2f}"
    k2 = f"  retention_rate={kpis.get('retention_rate', 0):.2f}"
    k3 = f"  pronunciation_score={kpis.get('pronunciation_score', 0):.2f}"
    k4 = f"  scenario_readiness={kpis.get('scenario_readiness', 0):.2f}"
    c1 = f"  lexicon={lx:.2f}"
    c2 = f"  comprehension={cm:.2f}"
    c3 = f"  pronunciation={pr:.2f}"
    c4 = f"  dialog_scenario={dg:.2f}"
    lines = [
        "KPI:",
        k1,
        k2,
        k3,
        k4,
        "Компетенции [0–1]:",
        c1,
        c2,
        c3,
        c4,
        f"Готовность к поездке: {tr.get('percent', 0):.1f}%",
    ]
    return "\n".join(lines)


def apply_global_ui_fonts(
    root: tk.Tk,
    *,
    delta_pt: int = 2,
    theme_variant: Literal["light", "dark"] = "light",
) -> None:
    """
    Кегль шрифтов + палитра и тема ttk (clam).

    ``delta_pt``: на сколько пунктов увеличить базовый кегль именованных шрифтов
    Tk (положительное — крупнее интерфейс, 0 — системный размер по умолчанию).

    ``theme_variant``: ``light`` / ``dark`` — светлая или тёмная палитра
    (см. ``theme.py``, словари ``PALETTE_*``).
    """
    names = (
        "TkDefaultFont",
        "TkTextFont",
        "TkFixedFont",
        "TkMenuFont",
        "TkHeadingFont",
        "TkCaptionFont",
        "TkSmallCaptionFont",
        "TkIconFont",
    )
    for name in names:
        try:
            f = tkfont.nametofont(name)
            f.configure(size=max(6, f.cget("size") + delta_pt))
        except tk.TclError:
            pass
    apply_professional_theme(
        root,
        variant="light" if theme_variant == "light" else "dark",
    )


class LearningDesktopApp:
    """Главное окно: параметры сессии, чат, демо-прогресс."""

    def __init__(
        self,
        root: tk.Tk,
        *,
        repo: ProgressRepository | None = None,
        initial_user_id: str | None = None,
    ) -> None:
        self._root = root
        self._initial_user_id = initial_user_id
        root.title("lang_learn")
        # Минимальный размер: окно нельзя сжать меньше (ширина x высота в пикселях).
        root.minsize(960, 520)
        # Стартовый размер при открытии (можно изменить под свой монитор).
        root.geometry("1150x980")

        self._prior: tuple[ChatMessage, ...] = ()
        self._repo = repo if repo is not None else open_gui_sqlite_progress_repository()
        self._user_id = _DEFAULT_GUI_USER_ID
        self._refresh_pending = False
        root.protocol("WM_DELETE_WINDOW", self._on_window_delete)

        self._registry = create_default_registry(with_audio_extras=False)

        try:
            stored_profile = self._build_form(root)
        except BaseException:
            self._repo.close()
            raise

        if stored_profile is not None:
            self._apply_session_fields_from_profile(stored_profile)
        else:
            self._init_user_profile()

    def _on_window_delete(self) -> None:
        """Закрыть БД и окно (повторные вызовы SQLite допускает)."""
        try:
            self._repo.close()
        finally:
            self._root.destroy()

    def _apply_llm_provider(self, name: str) -> None:
        """Переключить оркестратор диалога на выбранный LLM и сохранить выбор."""
        key = (name or "").strip().lower()
        if not key:
            return
        try:
            llm = self._registry.create_llm(key)
        except KeyError:
            messagebox.showerror(
                "Провайдер LLM",
                f"Неизвестный провайдер: {name!r}. Доступны: "
                f"{', '.join(self._registry.list_llm())}",
            )
            return
        self._orch = DialogOrchestrator(llm)
        self._llm_config = LLMProviderConfig(model=key)
        write_llm_provider_choice(key)

    def _on_llm_provider_selected(self, _event: tk.Event | None = None) -> None:
        self._apply_llm_provider(self._llm_var.get())

    def _init_user_profile(self) -> None:
        """Профиль A0; попытки появляются только из урока и диалога."""
        self._repo.save_profile(
            LearningProfile(
                user_id=self._user_id,
                interface_language="ru-RU",
                target_language="en-US",
                level_hint="a0",
            ),
        )

    def _apply_session_fields_from_profile(self, profile: LearningProfile) -> None:
        """Подставить в поля формы язык и уровень из сохранённого профиля."""
        lang = (profile.target_language or "").strip()
        if lang:
            self._lang.delete(0, tk.END)
            self._lang.insert(0, lang)
        hint = (profile.level_hint or "").strip()
        if hint:
            self._level.delete(0, tk.END)
            self._level.insert(0, hint.upper() if len(hint) <= 4 else hint)

    def _build_form(self, root: tk.Tk) -> LearningProfile | None:
        pal = getattr(root, "_lang_learn_palette", None) or {}
        fg = pal.get("fg", "#000000")

        # padding (гориз., верт.): внутренний отступ корневого фрейма от края окна.
        outer = ttk.Frame(root, style="App.TFrame", padding=(1, 1))
        outer.pack(fill=tk.BOTH, expand=True)

        par = ttk.LabelFrame(
            outer,
            text="Параметры сессии",
            style="Session.TLabelframe",
            # Отступ заголовка/содержимого внутри рамки «Параметры сессии».
            padding=(1, 1),
        )
        par.pack(fill=tk.X)

        ttk.Label(par, text="Пользователь (id)", style="Session.TLabel").grid(
            row=0, column=0, sticky=tk.W
        )
        # width у Entry/Combobox — условная ширина в символах (не пиксели).
        self._user_entry = ttk.Entry(par, width=36)
        seed_uid = (self._initial_user_id or "").strip() or _DEFAULT_GUI_USER_ID
        self._user_entry.insert(0, seed_uid)
        self._user_entry.grid(
            row=0, column=1, columnspan=3, sticky=tk.EW, padx=(4, 0)
        )

        self._user_id = normalize_session_user_id(self._user_entry.get())
        stored_profile = self._repo.load_profile(self._user_id)

        ttk.Label(par, text="Тема", style="Session.TLabel").grid(
            row=1, column=0, sticky=tk.W, pady=(2, 0)
        )
        self._topic = ttk.Entry(par, width=52)
        self._topic.insert(0, "Английский алфавит: буквы, написание, звучание")
        self._topic.grid(
            row=1, column=1, columnspan=3, sticky=tk.EW, padx=(4, 0), pady=(2, 0)
        )

        ttk.Label(par, text="Цель сессии", style="Session.TLabel").grid(
            row=2, column=0, sticky=tk.NW, pady=(1, 0)
        )
        # height — число строк текста; pady в grid — отступ строки от соседних.
        self._goal = tk.Text(par, height=3, width=50, wrap=tk.WORD)
        self._goal.insert(
            "1.0",
            "1) Узнать алфавит (латиница A–Z): порядок букв.\n"
            "2) Связать букву с написанием (пропись/печатные формы).\n"
            "3) Произношение каждой буквы (название и звук в слове).\n"
            "4) Сочетания букв (например ch, sh, th): чтение и примеры слов.",
        )
        self._goal.grid(
            row=2, column=1, columnspan=3, sticky=tk.EW, padx=(4, 0), pady=(1, 0)
        )

        ttk.Label(par, text="Уровень", style="Session.TLabel").grid(
            row=3, column=0, sticky=tk.W, pady=(1, 0)
        )
        self._level = ttk.Entry(par, width=8)
        self._level.insert(0, "A0")
        self._level.grid(row=3, column=1, sticky=tk.EW, padx=(4, 6), pady=(1, 0))

        ttk.Label(par, text="Целевой язык", style="Session.TLabel").grid(
            row=3, column=2, sticky=tk.W, pady=(1, 0)
        )
        self._lang = ttk.Entry(par, width=18)
        self._lang.insert(0, "en-US")
        self._lang.grid(row=3, column=3, sticky=tk.EW, padx=(4, 0), pady=(1, 0))

        llm_names = self._registry.list_llm()
        initial_llm = resolve_initial_llm_provider(
            llm_names,
            stored=read_llm_provider_choice(),
        )
        self._llm_var = tk.StringVar(value=initial_llm)
        ttk.Label(par, text="Провайдер LLM", style="Session.TLabel").grid(
            row=4, column=0, sticky=tk.W, pady=(1, 0)
        )
        self._llm_combo = ttk.Combobox(
            par,
            textvariable=self._llm_var,
            values=llm_names or ("stub",),
            state="readonly",
            width=28,
        )
        self._llm_combo.grid(row=4, column=1, sticky=tk.EW, padx=(4, 6), pady=(1, 0))
        self._llm_combo.bind(
            "<<ComboboxSelected>>",
            self._on_llm_provider_selected,
        )

        ttk.Label(par, text="Траектория", style="Session.TLabel").grid(
            row=4, column=2, sticky=tk.W, pady=(1, 0)
        )
        traj = TrajectoryService.load_default()
        ids = [s.id for s in traj.list_specs()]
        self._trajectory = tk.StringVar(value=ids[0] if ids else "travel")
        self._traj_combo = ttk.Combobox(
            par,
            textvariable=self._trajectory,
            values=ids or ("travel",),
            state="readonly",
            width=30,
        )
        self._traj_combo.grid(row=4, column=3, sticky=tk.EW, padx=(4, 0), pady=(1, 0))

        self._apply_llm_provider(initial_llm)

        # weight: 0 — колонка по ширине содержимого; 1 — доля растягивается при
        # расширении окна (поля ввода в колонках 1 и 3).
        par.columnconfigure(0, weight=0)
        par.columnconfigure(1, weight=1)
        par.columnconfigure(2, weight=0)
        par.columnconfigure(3, weight=1)

        # Контейнер под «Параметры сессии»: две колонки (урок/диалог | результат).
        # Стилизация Content — фон середины окна, см. theme.py.
        mid = ttk.Frame(outer, style="Content.TFrame")
        # pady сверху — зазор под «Параметры сессии» (в пикселях).
        mid.pack(fill=tk.BOTH, expand=True, pady=(11, 0))
        # Пропорции колонок: слева (урок/диалог) шире, справа («Результат») уже.
        # Одних weight иногда недостаточно (виджеты внутри «просят» ширину), поэтому
        # дополнительно фиксируем ширину правой колонки как долю от общей.
        # Хотим визуально «сжать в 2 раза» относительно левой части:
        # при равных колонках это даёт примерно 75/25.
        # Немного расширяем правую колонку относительно текущей настройки (+25%):
        # 0.25 → 0.3125.
        result_fraction = 0.3125
        mid.columnconfigure(0, weight=1)
        mid.columnconfigure(1, weight=0)
        mid.rowconfigure(0, weight=1)

        def _on_mid_configure(event: tk.Event) -> None:
            w = int(getattr(event, "width", 0) or 0)
            if w <= 0:
                return
            right_px = max(275, int(w * result_fraction))
            mid.columnconfigure(1, minsize=right_px)
            # Фиксируем ширину контейнера «Результат», чтобы его содержимое не
            # расширяло колонку (grid propagation).
            right.configure(width=right_px)

        # Важно: обработчик использует переменную right ниже — bind после создания.

        left = ttk.Frame(mid, style="Content.TFrame")
        left.grid(row=0, column=0, sticky=tk.NSEW, padx=(0, 8))
        left.rowconfigure(0, weight=1)
        left.columnconfigure(0, weight=1)

        right = ttk.Frame(mid, style="Content.TFrame")
        right.grid(row=0, column=1, sticky=tk.NSEW)
        right.grid_propagate(False)
        right.rowconfigure(0, weight=2)
        right.rowconfigure(1, weight=3)
        right.columnconfigure(0, weight=1)

        mid.bind("<Configure>", _on_mid_configure)

        nb = ttk.Notebook(left)
        nb.grid(row=0, column=0, sticky=tk.NSEW)

        # Внутренние отступы содержимого каждой вкладки.
        tab_alpha = ttk.Frame(nb, style="Card.TFrame", padding=(1, 1))
        tab_chat = ttk.Frame(nb, style="Card.TFrame", padding=(1, 1))
        nb.add(tab_alpha, text="Урок 1: алфавит")
        nb.add(tab_chat, text="Свободный диалог")

        PreA0AlphabetLesson(
            tab_alpha,
            user_id=self._user_id,
            repo=self._repo,
            on_attempt_saved=self._refresh_progress,
            voice_language_cb=lambda: self._lang.get(),
        ).pack(fill=tk.BOTH, expand=True)

        chat_fr = ttk.LabelFrame(
            tab_chat,
            text="Диалог с ИИ",
            style="OnCard.TLabelframe",
            padding=(1, 1),
        )
        chat_fr.pack(fill=tk.BOTH, expand=True)

        # Минимальная высота области чата в строках текста (прокрутка при переполнении).
        self._chat = ScrolledText(chat_fr, height=7, wrap=tk.WORD, state=tk.DISABLED)
        self._chat.pack(fill=tk.BOTH, expand=True)
        self._append_chat(
            "Система",
            "Вкладка «Урок 1: алфавит» — основной сценарий: задания из курса "
            "Pre-A0 (буквы, произношение по эталону, сочетания). Переключать "
            "режимы — вкладками внизу формы; на вкладке алфавита — блок "
            "«Переход к упражнению» для выбора шага очереди.\n\n"
            f"Во «Свободном диалоге» выбран провайдер LLM: «{self._llm_var.get()}» "
            "(список из реестра приложения). Для настоящей модели позже "
            "появятся дополнительные провайдеры.\n\n"
            "Тема и цель сверху относятся к этому чату; отправка — "
            "«Отправить» или Enter.",
        )

        inp_fr = ttk.Frame(chat_fr, style="OnCard.TFrame")
        inp_fr.pack(fill=tk.X, pady=(1, 0))
        ttk.Label(inp_fr, text="Ваш ответ", style="OnCard.TLabel").pack(
            side=tk.LEFT,
            padx=(0, 4),
        )
        self._input = ttk.Entry(inp_fr)
        self._input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))
        self._input.bind("<Return>", self._on_send_enter)
        ttk.Button(
            inp_fr,
            text="Отправить",
            style="Accent.TButton",
            command=self._on_send,
        ).pack(side=tk.RIGHT)

        cmp_fr = ttk.LabelFrame(
            right,
            text="Сравнение и рекомендации",
            style="Progress.TLabelframe",
            padding=(1, 1),
        )
        cmp_fr.grid(row=0, column=0, sticky=tk.NSEW, pady=(0, 8))
        cmp_fr.rowconfigure(0, weight=1)
        cmp_fr.columnconfigure(0, weight=1)
        self._compare = ScrolledText(cmp_fr, height=7, wrap=tk.WORD, state=tk.DISABLED)
        self._compare.grid(row=0, column=0, sticky=tk.NSEW)

        prog_fr = ttk.LabelFrame(
            right,
            text="Результат",
            style="Progress.TLabelframe",
            padding=(1, 1),
        )
        prog_fr.grid(row=1, column=0, sticky=tk.NSEW)
        prog_fr.rowconfigure(0, weight=1)
        prog_fr.columnconfigure(0, weight=1)
        # height ≈ число строк сводки (_overview_lines); меньше — появится скролл.
        self._progress = ScrolledText(
            prog_fr, height=9, wrap=tk.WORD, state=tk.DISABLED
        )
        self._progress.grid(row=0, column=0, sticky=tk.NSEW)
        ttk.Button(
            prog_fr,
            text="Обновить сводку",
            style="Muted.TButton",
            command=self._refresh_progress,
        ).grid(row=1, column=0, sticky=tk.E, pady=(1, 0))
        self._refresh_progress()

        if pal:
            style_text_widget(self._chat, pal)
            style_text_widget(self._compare, pal)
            style_text_widget(self._progress, pal)
            style_text_widget(self._goal, pal)
        else:
            for w in (self._chat, self._compare, self._progress, self._goal):
                try:
                    w.configure(foreground=fg)
                except tk.TclError:
                    pass

        return stored_profile

    def _on_send_enter(self, _event: tk.Event) -> str:
        self._on_send()
        return "break"

    def _append_chat(self, role: str, text: str) -> None:
        self._chat.configure(state=tk.NORMAL)
        self._chat.insert(tk.END, f"{role}:\n{text}\n\n")
        self._chat.see(tk.END)
        self._chat.configure(state=tk.DISABLED)

    def _refresh_progress(self) -> None:
        """Запросить обновление правой колонки (всегда в UI-потоке)."""
        if self._refresh_pending:
            return
        self._refresh_pending = True
        self._root.after_idle(self._refresh_progress_ui)

    def _refresh_progress_ui(self) -> None:
        self._refresh_pending = False
        attempts = self._repo.list_attempts(self._user_id, limit=100)
        self._compare.configure(state=tk.NORMAL)
        self._compare.delete("1.0", tk.END)
        if attempts:
            a0 = attempts[0]
            ref = (a0.details.get("reference_text") if a0.details else None) or ""
            rec = (
                (a0.details.get("recommendation_next") if a0.details else None) or ""
            )
            score = float(a0.score or 0.0)
            tr = (a0.transcript or "").strip()
            lines = [
                f"Упражнение: {a0.exercise_id}",
                f"Оценка: {score:.2f}",
            ]
            if ref:
                lines += ["", "Эталон:", str(ref)]
            if tr:
                lines += ["", "Ваш ответ:", tr]
            if rec:
                lines += ["", "Рекомендация:", str(rec)]
            self._compare.insert(tk.END, "\n".join(lines))
        else:
            self._compare.insert(tk.END, "Пока нет попыток — выполните упражнение.")
        self._compare.configure(state=tk.DISABLED)

        overview = compute_progress_overview(attempts)
        text = _overview_lines(overview.model_dump_json())
        self._progress.configure(state=tk.NORMAL)
        self._progress.delete("1.0", tk.END)
        self._progress.insert(tk.END, text)
        self._progress.configure(state=tk.DISABLED)

    def _on_send(self) -> None:
        raw = self._input.get().strip()
        if not raw:
            messagebox.showwarning("Пустой ввод", "Введите текст ответа.")
            return

        topic = self._topic.get().strip() or "Lesson"
        goal = self._goal.get("1.0", tk.END).strip() or "Practice"
        level = self._level.get().strip() or "A0"
        lang = self._lang.get().strip() or "en-US"

        self._append_chat("Вы", raw)
        self._input.delete(0, tk.END)

        ctx = DialogSessionContext(
            topic=topic,
            session_goal=goal,
            level_hint=level,
            target_language=cast(LanguageCode, lang),
            user_latest_message=raw,
            max_reply_sentences=3,
            prior_messages=self._prior,
        )
        try:
            result = self._orch.run_turn(ctx, self._llm_config)
        except Exception as exc:
            messagebox.showerror("Ошибка", str(exc))
            return

        rep = result.structured
        body = rep.assistant_reply
        if rep.corrections:
            lines = [
                f"  • {c.original_fragment!r} → {c.suggested!r}"
                for c in rep.corrections
            ]
            body += "\nПравки:\n" + "\n".join(lines)
        if rep.new_vocabulary:
            voc = ", ".join(f"{v.term} ({v.gloss})" for v in rep.new_vocabulary)
            body += f"\nЛексика: {voc}"
        self._append_chat("Ассистент", body)

        self._prior = append_turn_to_history(
            self._prior,
            user_text=raw,
            assistant_reply=rep.assistant_reply,
        )
        aid = f"gui-turn-{len(self._prior)}"
        self._repo.save_attempt(
            AttemptRecord(
                attempt_id=aid,
                user_id=self._user_id,
                exercise_id="dialog_turn",
                transcript=raw,
                score=0.62,
                details={
                    "skill_axis": "dialog_scenario",
                    "scenario_slug": self._trajectory.get(),
                    "llm_provider": self._llm_var.get().strip().lower(),
                },
            ),
        )
        self._repo.save_profile(
            LearningProfile(
                user_id=self._user_id,
                interface_language="ru-RU",
                target_language=cast(LanguageCode, lang),
                level_hint=level.lower(),
            ),
        )
        self._refresh_progress()


def run_learning_desktop() -> None:
    """Запустить главный цикл окна."""
    from lang_learn.config.dotenv_load import load_dotenv_files

    load_dotenv_files()

    root = tk.Tk()
    # delta_pt: +к системному кеглю (1 — чуть крупнее, 0 — как в ОС).
    apply_global_ui_fonts(root, delta_pt=1)
    try:
        LearningDesktopApp(root)
    except (FileNotFoundError, OSError) as exc:
        messagebox.showerror(
            "Хранилище прогресса",
            "Не удалось открыть или создать базу данных прогресса:\n"
            f"{exc}",
        )
        root.destroy()
        return
    root.mainloop()
