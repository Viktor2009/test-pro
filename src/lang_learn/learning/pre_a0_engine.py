"""Движок уроков Pre-A0: очередь упражнений и простой повтор при ошибках."""

from __future__ import annotations

from collections import defaultdict

from lang_learn.contracts.lesson import LessonEngine
from lang_learn.learning import pronunciation
from lang_learn.schemas.learning import (
    AttemptFeedback,
    AttemptRecord,
    ExercisePayload,
    LessonContext,
)
from lang_learn.schemas.pre_a0 import ExerciseKind, PreA0Course


class PreA0LessonEngine(LessonEngine):
    """
    Линейная выдача упражнений по курсу + стек повтора при низкой оценке.

    Порог принятия ответа задаётся ``accept_threshold`` (по умолчанию 0.55).
    """

    def __init__(
        self,
        course: PreA0Course,
        *,
        accept_threshold: float = 0.55,
    ) -> None:
        if not 0.0 < accept_threshold <= 1.0:
            msg = "accept_threshold must be in (0, 1]"
            raise ValueError(msg)
        self._course = course
        self._accept_threshold = accept_threshold
        self._queue, self._by_id = _build_queue(course)
        self._next_index: dict[str, int] = defaultdict(int)
        self._repeat_stack: dict[str, list[ExercisePayload]] = defaultdict(list)

    def next_exercise(self, ctx: LessonContext) -> ExercisePayload:
        """Следующее упражнение или повтор из стека."""
        uid = str(ctx.user_id)
        pending = self._repeat_stack[uid]
        if pending:
            return pending.pop()
        idx = self._next_index[uid]
        if idx >= len(self._queue):
            idx = 0
        ex = self._queue[idx]
        self._next_index[uid] = idx + 1
        return ex

    def submit_attempt(self, attempt: AttemptRecord) -> AttemptFeedback:
        """
        Оценить попытку по эталону и при необходимости запланировать повтор.
        """
        ex = self._by_id.get(str(attempt.exercise_id))
        if ex is None:
            return AttemptFeedback(
                accepted=False,
                summary="Неизвестное упражнение.",
                next_hint=None,
            )
        transcript = (attempt.transcript or "").strip()
        if not transcript:
            # Пустой ввод не кладём в стек повтора: иначе при «дребезге» Enter
            # одно и то же упражнение дублируется в стеке несколько раз подряд.
            return AttemptFeedback(
                accepted=False,
                summary="Пустой ответ.",
                next_hint="Введите текст и снова нажмите «Проверить».",
            )

        if ex.kind == ExerciseKind.RECOGNIZE_LETTER.value:
            h_spaced = pronunciation.normalize_utterance(transcript)
            h_one = h_spaced.replace(" ", "")
            # STT иногда возвращает "b b b" → "bbb" для одной буквы.
            # Важно: "aa"/"Aa" (без разделителей) — это уже две буквы, не сжимаем.
            if " " in h_spaced and len(h_one) > 1 and len(set(h_one)) == 1:
                h_one = h_one[0]
            if len(h_one) != 1:
                self._repeat_stack[str(attempt.user_id)].append(ex)
                return AttemptFeedback(
                    accepted=False,
                    summary="Ожидается одна буква.",
                    next_hint=(
                        "Введите ровно одну латинскую букву. Регистр не важен "
                        "(A и a — одно и то же); достаточно одного ответа."
                    ),
                )
            correct = str(ex.metadata.get("correct", ex.reference_text or ""))
            c_one = pronunciation.normalize_utterance(correct).replace(" ", "")
            if not c_one:
                c_one = pronunciation.normalize_utterance(
                    str(ex.reference_text or ""),
                ).replace(" ", "")
            if len(c_one) == 1 and h_one == c_one:
                return AttemptFeedback(
                    accepted=True,
                    summary="Верно (регистр буквы не учитывается).",
                    next_hint=None,
                )

        ref = _reference_for_scoring(ex)
        score = pronunciation.utterance_similarity(ref, transcript)
        keys = _key_graphemes(ex)
        missing = pronunciation.missing_key_graphemes(transcript, keys)
        if short_grapheme_answer_matches(ex, transcript):
            # Эталон «A apple», но ответ только «A»/«a» — для начинающих засчитываем.
            score = 1.0
            missing = []
        accepted = score >= self._accept_threshold and not missing

        if not accepted:
            self._repeat_stack[str(attempt.user_id)].append(ex)
            hint = _hint_for_retry(ex, missing, score)
            summary = (
                f"Оценка {score:.2f}; порог {self._accept_threshold:.2f}. "
                f"Пропуски: {', '.join(missing) if missing else '—'}"
            )
            return AttemptFeedback(
                accepted=False,
                summary=summary,
                next_hint=hint,
            )

        return AttemptFeedback(
            accepted=True,
            summary=f"Хорошо (оценка {score:.2f}).",
            next_hint=None,
        )

    def exercise_menu_entries(self) -> tuple[tuple[str, str], ...]:
        """Пары ``(exercise_id, краткая подпись)`` в порядке очереди урока."""
        return tuple(
            (str(ex.exercise_id), _short_label_for_exercise(ex))
            for ex in self._queue
        )

    def seek_user_to_exercise(self, user_id: str, exercise_id: str) -> bool:
        """
        Сбросить стек повтора и поставить очередь на выбранное упражнение.

        Следующий вызов ``next_exercise`` для этого пользователя вернёт шаг
        с данным ``exercise_id``. Неизвестный id — ``False``.
        """
        eid = str(exercise_id)
        if eid not in self._by_id:
            return False
        uid = str(user_id)
        self._repeat_stack[uid].clear()
        for i, ex in enumerate(self._queue):
            if str(ex.exercise_id) == eid:
                self._next_index[uid] = i
                return True
        return False


def short_grapheme_answer_matches(ex: ExercisePayload, transcript: str) -> bool:
    """
    Ответ совпадает с ключевой графемой (регистр не важен): одна буква или ch и т.д.

    Для шага «слушай и повтори» по букве эталон полный («A apple»), а ввод «A»
    должен оставаться верным.
    """
    if ex.kind not in (
        ExerciseKind.LISTEN_REPEAT.value,
        ExerciseKind.READ_ALOUD_COMPARE.value,
    ):
        return False
    if ex.metadata.get("pair_id"):
        return False
    if not (ex.metadata.get("letter_id") or ex.metadata.get("cluster_id")):
        return False
    raw_g = ex.metadata.get("grapheme")
    if not isinstance(raw_g, str) or not raw_g.strip():
        return False
    g_norm = pronunciation.normalize_utterance(raw_g).replace(" ", "")
    h_spaced = pronunciation.normalize_utterance(transcript)
    h_norm = h_spaced.replace(" ", "")
    if not h_norm:
        return False
    # STT иногда возвращает "b b b" для произнесённой буквы "B".
    # Для одиночных графем допускаем повтор одного и того же символа.
    if (
        len(g_norm) == 1
        and " " in h_spaced
        and len(h_norm) > 1
        and len(set(h_norm)) == 1
    ):
        h_norm = h_norm[0]
    if len(h_norm) != len(g_norm):
        return False
    return h_norm == g_norm


def _ipa_clause(ipa: str) -> str:
    """Фрагмент с IPA для текста задания; пустая строка не показывается."""
    t = (ipa or "").strip()
    return f" ({t})" if t else ""


def _short_label_for_exercise(ex: ExercisePayload) -> str:
    """Короткая подпись для списка выбора в UI отладки."""
    kind = ex.kind
    mid = ex.metadata or {}
    if mid.get("pair_id"):
        ref = (ex.reference_text or "").strip()
        return f"мин. пара — «{ref}» (слушай)" if ref else str(ex.exercise_id)
    grapheme = mid.get("grapheme")
    if isinstance(grapheme, str) and grapheme.strip():
        g = grapheme.strip()
        if kind == ExerciseKind.LISTEN_REPEAT.value:
            return f"«{g}» — слушай и повтори"
        if kind == ExerciseKind.READ_ALOUD_COMPARE.value:
            return f"«{g}» — прочитай"
        if kind == ExerciseKind.RECOGNIZE_LETTER.value:
            return f"«{g}» — узнай букву"
    return str(ex.exercise_id)


def _build_queue(
    course: PreA0Course,
) -> tuple[list[ExercisePayload], dict[str, ExercisePayload]]:
    items: list[ExercisePayload] = []
    by_id: dict[str, ExercisePayload] = {}

    def push(ex: ExercisePayload) -> None:
        items.append(ex)
        by_id[str(ex.exercise_id)] = ex

    for letter in course.letters:
        listen = ExercisePayload(
            exercise_id=f"prea0.{letter.id}.listen",
            kind=ExerciseKind.LISTEN_REPEAT.value,
            instructions=(
                f"Прослушайте и повторите: буква {letter.grapheme}"
                f"{_ipa_clause(letter.ipa)} как в слове «{letter.example_word}»."
            ),
            reference_text=f"{letter.grapheme} {letter.example_word}",
            metadata={
                "letter_id": letter.id,
                "ipa": letter.ipa,
                "grapheme": letter.grapheme,
            },
        )
        push(listen)
        read_ex = ExercisePayload(
            exercise_id=f"prea0.{letter.id}.read",
            kind=ExerciseKind.READ_ALOUD_COMPARE.value,
            instructions=(
                f"Прочитайте вслух букву {letter.grapheme} "
                f"(как в «{letter.example_word}»)."
            ),
            reference_text=letter.grapheme,
            metadata={"letter_id": letter.id, "grapheme": letter.grapheme},
        )
        push(read_ex)
        distractors = _distractor_graphemes(course, letter.grapheme)
        rec = ExercisePayload(
            exercise_id=f"prea0.{letter.id}.pick",
            kind=ExerciseKind.RECOGNIZE_LETTER.value,
            instructions=(
                "Введите правильную букву (ровно один символ). "
                "Заглавная и строчная латиница (A и a) считаются верным ответом."
            ),
            reference_text=letter.grapheme,
            metadata={
                "letter_id": letter.id,
                "options": [letter.grapheme] + distractors,
                "correct": letter.grapheme,
            },
        )
        push(rec)

    for cl in course.clusters:
        listen = ExercisePayload(
            exercise_id=f"prea0.{cl.id}.listen",
            kind=ExerciseKind.LISTEN_REPEAT.value,
            instructions=(
                f"Прослушайте и повторите сочетание «{cl.grapheme}»"
                f"{_ipa_clause(cl.ipa)} в слове «{cl.example_word}»."
            ),
            reference_text=f"{cl.grapheme} {cl.example_word}",
            metadata={"cluster_id": cl.id, "grapheme": cl.grapheme},
        )
        push(listen)
        read_ex = ExercisePayload(
            exercise_id=f"prea0.{cl.id}.read",
            kind=ExerciseKind.READ_ALOUD_COMPARE.value,
            instructions=f"Прочитайте вслух «{cl.grapheme}».",
            reference_text=cl.grapheme,
            metadata={"cluster_id": cl.id, "grapheme": cl.grapheme},
        )
        push(read_ex)

    for pair in course.minimal_pairs:
        listen = ExercisePayload(
            exercise_id=f"prea0.{pair.id}.listen_a",
            kind=ExerciseKind.LISTEN_REPEAT.value,
            instructions=(
                f"Прослушайте и повторите слово «{pair.word_a}» "
                f"(пара: {pair.word_a} / {pair.word_b}, {pair.focus})."
            ),
            reference_text=pair.word_a,
            metadata={"pair_id": pair.id, "focus": pair.focus},
        )
        push(listen)

    return items, by_id


def _distractor_graphemes(course: PreA0Course, current: str) -> list[str]:
    pool = [L.grapheme for L in course.letters if L.grapheme != current]
    out: list[str] = []
    for g in pool:
        if g not in out:
            out.append(g)
        if len(out) >= 2:
            break
    while len(out) < 2:
        out.append("?")
    return out[:2]


def _reference_for_scoring(ex: ExercisePayload) -> str:
    if ex.kind == ExerciseKind.RECOGNIZE_LETTER.value:
        correct = str(ex.metadata.get("correct", ex.reference_text or ""))
        return correct
    return ex.reference_text or ""


def _key_graphemes(ex: ExercisePayload) -> list[str]:
    g = ex.metadata.get("grapheme")
    if isinstance(g, str) and g:
        return [g]
    if ex.kind == ExerciseKind.RECOGNIZE_LETTER.value:
        c = ex.metadata.get("correct")
        if isinstance(c, str) and c:
            return [c]
    return []


def _hint_for_retry(
    ex: ExercisePayload,
    missing: list[str],
    score: float,
) -> str:
    if missing:
        return f"Сделайте акцент на: {', '.join(missing)}"
    if ex.reference_text:
        return f"Постарайтесь ближе к: «{ex.reference_text}» (сейчас {score:.2f})"
    return "Повторите упражнение ещё раз."
