"""CLI: диагностика устройств, TTS, запись, STT (этап 1)."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Callable
from pathlib import Path
from typing import cast


def _cmd_devices(_args: argparse.Namespace) -> int:
    from lang_learn.audio_io.devices import list_audio_devices

    for d in list_audio_devices():
        tag = []
        if d.max_input_channels > 0:
            tag.append("in")
        if d.max_output_channels > 0:
            tag.append("out")
        caps = ",".join(tag) or "-"
        sr = d.default_samplerate or 0.0
        print(f"[{d.index}] {d.name}  ({caps})  default_sr={sr:.0f}")
    return 0


def _cmd_speak(args: argparse.Namespace) -> int:
    from lang_learn.audio_io.playback import play_wav_bytes
    from lang_learn.providers.pyttsx3_tts import Pyttsx3TTSProvider
    from lang_learn.schemas.audio import TTSRequest

    prov = Pyttsx3TTSProvider()
    req = TTSRequest(
        text=args.text,
        language=args.lang,
        voice_id=args.voice,
        speed=args.speed,
    )
    result = prov.synthesize(req)
    if args.out:
        Path(args.out).write_bytes(result.audio)
        print(f"WAV записан: {args.out}")
    if not args.no_play:
        play_wav_bytes(result.audio)
    return 0


def _cmd_record(args: argparse.Namespace) -> int:
    from lang_learn.audio_io.recorder import MicrophoneRecorder

    rec = MicrophoneRecorder(
        sample_rate_hz=args.sample_rate,
        device=args.device,
    )
    data = rec.record_seconds(args.seconds)
    Path(args.out).write_bytes(data)
    print(f"Записано {len(data)} байт в {args.out}")
    return 0


def _cmd_dialog_demo(_args: argparse.Namespace) -> int:
    """Один ход учебного диалога (StubLLM + структурированный JSON)."""
    from lang_learn.learning.dialog_orchestrator import DialogOrchestrator
    from lang_learn.providers.stub_llm import StubLLMProvider
    from lang_learn.schemas.dialog import DialogSessionContext
    from lang_learn.schemas.llm import LLMProviderConfig

    orch = DialogOrchestrator(StubLLMProvider())
    ctx = DialogSessionContext(
        topic="Airport check-in",
        session_goal="Short questions and answers at the counter.",
        level_hint="A1",
        target_language="en-US",
        user_latest_message="Where is gate B12?",
        max_reply_sentences=2,
    )
    out = orch.run_turn(ctx, LLMProviderConfig(model="stub"))
    print(out.structured.model_dump_json(indent=2))
    print("fallback_used:", out.fallback_used)
    return 0


def _cmd_prea0_demo(_args: argparse.Namespace) -> int:
    """
    Демонстрация Pre-A0-движка в одном процессе (без сохранения состояния).
    """
    from lang_learn.learning.course_loader import load_packaged_en_sample
    from lang_learn.learning.pre_a0_engine import PreA0LessonEngine
    from lang_learn.schemas.learning import AttemptRecord, LessonContext

    eng = PreA0LessonEngine(load_packaged_en_sample())
    uid = "demo-user"
    ctx = LessonContext(user_id=uid)
    ex = eng.next_exercise(ctx)
    print("Упражнение:", ex.exercise_id, ex.kind)
    md = ex.metadata
    transcript = (ex.reference_text or "").strip() or str(
        md.get("correct") or md.get("grapheme") or "A",
    )
    fb = eng.submit_attempt(
        AttemptRecord(
            attempt_id="demo-attempt-1",
            user_id=uid,
            exercise_id=ex.exercise_id,
            transcript=transcript,
        ),
    )
    print("Фидбек:", fb.accepted, fb.summary)
    ex2 = eng.next_exercise(ctx)
    print("Следующее:", ex2.exercise_id)
    return 0


def _cmd_transcribe(args: argparse.Namespace) -> int:
    from lang_learn.providers.faster_whisper_stt import FasterWhisperSTTProvider
    from lang_learn.schemas.audio import STTRequest

    wav = Path(args.wav).read_bytes()
    prov = FasterWhisperSTTProvider(model_size=args.model)
    req = STTRequest(audio=wav, language=args.lang)
    res = prov.transcribe(req)
    print(res.text)
    if res.confidence is not None:
        print(f"confidence={res.confidence:.3f}")
    return 0


def _cmd_travel_list(_args: argparse.Namespace) -> int:
    from lang_learn.learning.travel_session import TravelScenarioService

    svc = TravelScenarioService.load_default()
    for sc in svc.list_scenarios():
        print(f"{sc.slug}\t{sc.title}")
    return 0


def _cmd_travel_survival(args: argparse.Namespace) -> int:
    from lang_learn.learning.travel_session import TravelScenarioService

    svc = TravelScenarioService.load_default()
    for p in svc.survival_phrases(args.slug):
        print(f"- {p.text}  ({p.gloss})")
    return 0


def _cmd_travel_demo(args: argparse.Namespace) -> int:
    """Диалог по travel-сценарию (StubLLM)."""
    from lang_learn.learning.dialog_orchestrator import DialogOrchestrator
    from lang_learn.learning.travel_session import TravelScenarioService
    from lang_learn.providers.stub_llm import StubLLMProvider
    from lang_learn.schemas.llm import LLMProviderConfig

    svc = TravelScenarioService.load_default()
    ctx = svc.build_dialog_context(
        args.slug,
        args.message,
        variation_level=args.variation,
        stress=args.stress,
    )
    out = DialogOrchestrator(StubLLMProvider()).run_turn(
        ctx,
        LLMProviderConfig(model="stub"),
    )
    print(out.structured.model_dump_json(indent=2))
    print("stress:", args.stress, "variation:", args.variation)
    return 0


def _cmd_pronunciation_report(args: argparse.Namespace) -> int:
    from lang_learn.learning.speech_quality import analyze_pronunciation

    rep = analyze_pronunciation(
        args.ref,
        args.hyp,
        reference_audio_duration_ms=args.ref_ms,
        hypothesis_audio_duration_ms=args.hyp_ms,
    )
    print(rep.model_dump_json(indent=2))
    return 0


def _cmd_shadowing_plan(args: argparse.Namespace) -> int:
    from lang_learn.learning.shadowing import build_shadowing_plan

    plan = build_shadowing_plan(
        args.text,
        tempo=args.tempo,
        rounds=args.rounds,
    )
    print(plan.model_dump_json(indent=2))
    return 0


def _cmd_phrase_progress(args: argparse.Namespace) -> int:
    from lang_learn.learning.phrase_progress import summarize_phrase_progress
    from lang_learn.schemas.speech_quality import PhraseScoreLog

    parts = [p.strip() for p in args.scores.split(",") if p.strip()]
    scores = tuple(float(x) for x in parts)
    log = PhraseScoreLog(phrase_id=args.phrase_id, composite_scores=scores)
    print(summarize_phrase_progress(log))
    return 0


def _cmd_progress_demo(args: argparse.Namespace) -> int:
    """SQLite + KPI + travel readiness + постановка в очередь повторений."""
    import json
    from pathlib import Path

    from lang_learn.learning.progress_report import compute_progress_overview
    from lang_learn.learning.srs_planner import plan_review_items, weak_skill_axes
    from lang_learn.persistence.sqlite_progress import SqliteProgressRepository
    from lang_learn.schemas.learning import AttemptRecord, LearningProfile

    root = Path(__file__).resolve().parent.parent.parent
    schema_path = Path(args.schema) if args.schema else root / "db" / "schema.sql"
    schema_sql = schema_path.read_text(encoding="utf-8")
    repo = SqliteProgressRepository(Path(args.db), schema_sql=schema_sql)
    try:
        uid = args.user
        repo.save_profile(
            LearningProfile(
                user_id=uid,
                interface_language="ru-RU",
                target_language="en-US",
                level_hint="a1",
            ),
        )
        seeds: list[tuple[str, float, dict[str, object]]] = [
            (
                "ex-a1",
                0.62,
                {"scenario_slug": "airport", "skill_axis": "dialog_scenario"},
            ),
            ("ex-a2", 0.58, {"scenario_slug": "hotel", "skill_axis": "lexicon"}),
            ("ex-p1", 0.45, {"skill_axis": "pronunciation"}),
            ("ex-c1", 0.71, {"skill_axis": "comprehension"}),
        ]
        for i, (eid, score, det) in enumerate(seeds):
            repo.save_attempt(
                AttemptRecord(
                    attempt_id=f"seed-{i}",
                    user_id=uid,
                    exercise_id=eid,
                    transcript="demo",
                    score=score,
                    details=det,
                ),
            )
        attempts = repo.list_attempts(uid)
        overview = compute_progress_overview(attempts)
        print(overview.model_dump_json(indent=2))
        weak = weak_skill_axes(overview.competency, threshold=args.threshold)
        plan = plan_review_items(weak, base_hours=args.srs_hours)
        print("review_plan:", json.dumps(plan, ensure_ascii=False))
        for kind, ref, due in plan:
            repo.enqueue_review(
                uid,
                due_utc=due,
                item_kind=kind,
                item_ref=ref,
                payload={},
            )
        print("enqueued_reviews:", len(plan))
    finally:
        repo.close()
    return 0


def _cmd_ext_demo(args: argparse.Namespace) -> int:
    """Флаги, реестры провайдеров и движков, траектории (этап 7)."""
    import json

    from lang_learn.config.feature_flags import load_feature_flags
    from lang_learn.learning.trajectory_service import TrajectoryService
    from lang_learn.learning.travel_session import TravelScenarioService
    from lang_learn.plugins.bootstrap import (
        create_default_lesson_engine_registry,
        create_default_registry,
        register_audio_providers,
    )

    flags = load_feature_flags()
    print("feature_flags:", json.dumps(flags.as_dict(), ensure_ascii=False, indent=2))

    prov_reg = create_default_registry(with_audio_extras=False)
    if args.with_audio:
        try:
            register_audio_providers(prov_reg)
        except ImportError as exc:
            print("Не удалось подключить audio-провайдеры:", exc)
            return 1
    print(
        "providers llm:",
        list(prov_reg.list_llm()),
        "stt:",
        list(prov_reg.list_stt()),
        "tts:",
        list(prov_reg.list_tts()),
    )

    eng = create_default_lesson_engine_registry()
    print("lesson_engines:", list(eng.list_names()))

    ts = TrajectoryService.load_default()
    travel = TravelScenarioService.load_default()
    known = frozenset(s.slug for s in travel.list_scenarios())
    for spec in ts.list_specs():
        unk = ts.unknown_scenario_slugs(spec, known)
        extra = f"\tunknown_slugs={list(unk)}" if unk else ""
        print(
            f"{spec.id}\t{spec.title}\tscenarios={list(spec.scenario_slugs)}{extra}",
        )
    return 0


def _cmd_gui(_args: argparse.Namespace) -> int:
    """Графическое окно учебного диалога (этап 8, tkinter)."""
    from lang_learn.gui.desktop_chat import run_learning_desktop

    run_learning_desktop()
    return 0


def _cmd_integration_dialog(args: argparse.Namespace) -> int:
    """Один ход диалога: Http DTO → домен → Http ответ (этап 7)."""
    from lang_learn.learning.dialog_orchestrator import DialogOrchestrator
    from lang_learn.plugins.bootstrap import create_default_registry
    from lang_learn.schemas.integration_api import (
        HttpDialogTurnRequest,
        HttpDialogTurnResponse,
    )
    from lang_learn.schemas.llm import LLMProviderConfig

    req = HttpDialogTurnRequest(
        topic=args.topic,
        session_goal=args.goal,
        level_hint=args.level,
        target_language=args.lang,
        user_latest_message=args.message,
        max_reply_sentences=args.max_sentences,
        llm_provider=args.llm,
    )
    reg = create_default_registry(with_audio_extras=False)
    llm = reg.create_llm(req.llm_provider)
    orch = DialogOrchestrator(llm)
    ctx = req.to_session_context()
    result = orch.run_turn(ctx, LLMProviderConfig(model="stub"))
    out = HttpDialogTurnResponse.from_turn_result(result)
    print(out.model_dump_json(indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="lang_learn",
        description=(
            "Изучение языка: аудио, Pre-A0, диалог, travel, произношение, "
            "прогресс, расширяемость (этап 7), GUI (этап 8)."
        ),
    )
    sub = p.add_subparsers(dest="cmd")

    p_dev = sub.add_parser("devices", help="Список аудиоустройств (PortAudio)")
    p_dev.set_defaults(handler=_cmd_devices)

    p_sp = sub.add_parser("speak", help="Синтез WAV (pyttsx3) и воспроизведение")
    p_sp.add_argument("--text", required=True)
    p_sp.add_argument("--lang", default="en-US")
    p_sp.add_argument("--voice", default=None)
    p_sp.add_argument("--speed", type=float, default=1.0)
    p_sp.add_argument("--out", default=None, help="Сохранить WAV в файл")
    p_sp.add_argument(
        "--no-play",
        action="store_true",
        help="Не воспроизводить, только синтез (и опционально --out)",
    )
    p_sp.set_defaults(handler=_cmd_speak)

    p_rec = sub.add_parser("record", help="Запись с микрофона в WAV")
    p_rec.add_argument("--seconds", type=float, required=True)
    p_rec.add_argument("--out", required=True)
    p_rec.add_argument("--sample-rate", type=int, default=16000, dest="sample_rate")
    p_rec.add_argument("--device", type=int, default=None)
    p_rec.set_defaults(handler=_cmd_record)

    p_tr = sub.add_parser("transcribe", help="STT из WAV (faster-whisper)")
    p_tr.add_argument("--wav", required=True)
    p_tr.add_argument("--lang", default=None)
    p_tr.add_argument("--model", default="tiny")
    p_tr.set_defaults(handler=_cmd_transcribe)

    p_demo = sub.add_parser(
        "prea0-demo",
        help="Демо одного цикла Pre-A0 (след. упражнение + эталонный ответ)",
    )
    p_demo.set_defaults(handler=_cmd_prea0_demo)

    p_dlg = sub.add_parser(
        "dialog-demo",
        help="Демо одного хода диалога (этап 3, StubLLM + JSON)",
    )
    p_dlg.set_defaults(handler=_cmd_dialog_demo)

    p_tl = sub.add_parser("travel-list", help="Список travel-сценариев (этап 4)")
    p_tl.set_defaults(handler=_cmd_travel_list)

    p_ts = sub.add_parser(
        "travel-survival",
        help="Карточка выживания: критические фразы по slug",
    )
    p_ts.add_argument("--slug", required=True)
    p_ts.set_defaults(handler=_cmd_travel_survival)

    p_td = sub.add_parser(
        "travel-demo",
        help="Диалог по сценарию (StubLLM), опции stress / variation",
    )
    p_td.add_argument("--slug", required=True)
    p_td.add_argument("--message", default="Hello, I need help.")
    p_td.add_argument(
        "--stress",
        action="store_true",
        help="Режим стресса (короче реплики, уточняющие вопросы в цели)",
    )
    p_td.add_argument("--variation", type=int, default=1, help="Уровень 1–5")
    p_td.set_defaults(handler=_cmd_travel_demo)

    p_pr = sub.add_parser(
        "pronunciation-report",
        help="Отчёт по произношению: эталон vs гипотеза (этап 5)",
    )
    p_pr.add_argument("--ref", required=True, help="Эталонный текст")
    p_pr.add_argument("--hyp", default="", help="Распознанный / произнесённый текст")
    p_pr.add_argument("--ref-ms", type=int, default=None, dest="ref_ms")
    p_pr.add_argument("--hyp-ms", type=int, default=None, dest="hyp_ms")
    p_pr.set_defaults(handler=_cmd_pronunciation_report)

    p_sh = sub.add_parser(
        "shadowing-plan",
        help="Параметры shadowing по тексту и темпу",
    )
    p_sh.add_argument("--text", required=True)
    p_sh.add_argument(
        "--tempo",
        choices=("slow", "normal", "fast"),
        default="normal",
    )
    p_sh.add_argument("--rounds", type=int, default=3)
    p_sh.set_defaults(handler=_cmd_shadowing_plan)

    p_pp = sub.add_parser(
        "phrase-progress",
        help="Сводка «до/после» по списку composite-оценок (через запятую)",
    )
    p_pp.add_argument("--phrase-id", required=True, dest="phrase_id")
    p_pp.add_argument("--scores", required=True, help="Например: 0.4,0.55,0.72")
    p_pp.set_defaults(handler=_cmd_phrase_progress)

    p_prog = sub.add_parser(
        "progress-demo",
        help="Демо прогресса: SQLite, KPI, готовность к поездке, SRS (этап 6)",
    )
    p_prog.add_argument(
        "--db",
        default=".lang_learn_progress_demo.sqlite",
        help="Файл SQLite (создаётся/дополняется)",
    )
    p_prog.add_argument(
        "--schema",
        default=None,
        help="Путь к schema.sql (по умолчанию db/schema.sql в корне проекта)",
    )
    p_prog.add_argument("--user", default="demo-user")
    p_prog.add_argument(
        "--threshold",
        type=float,
        default=0.55,
        help="Порог слабой компетенции для плана повторений",
    )
    p_prog.add_argument(
        "--srs-hours",
        type=int,
        default=24,
        dest="srs_hours",
        help="Базовый шаг часов между элементами плана",
    )
    p_prog.set_defaults(handler=_cmd_progress_demo)

    p_ext = sub.add_parser(
        "ext-demo",
        help="Этап 7: feature flags, реестры провайдеров/движков, траектории",
    )
    p_ext.add_argument(
        "--with-audio",
        action="store_true",
        help='Добавить pyttsx3 и faster_whisper (нужен pip install -e ".[audio]")',
    )
    p_ext.set_defaults(handler=_cmd_ext_demo)

    p_int = sub.add_parser(
        "integration-dialog",
        help="Этап 7: один ход диалога (формат Http DTO → JSON)",
    )
    p_int.add_argument("--topic", required=True)
    p_int.add_argument("--goal", required=True, help="Цель сессии")
    p_int.add_argument("--message", required=True, help="Реплика пользователя")
    p_int.add_argument("--level", default="A1")
    p_int.add_argument("--lang", default="en-US", dest="lang")
    p_int.add_argument("--llm", default="stub", help="Ключ из реестра LLM")
    p_int.add_argument(
        "--max-sentences",
        type=int,
        default=3,
        dest="max_sentences",
    )
    p_int.set_defaults(handler=_cmd_integration_dialog)

    p_gui = sub.add_parser(
        "gui",
        help="Этап 8: окно диалога с ИИ, уровень, прогресс (tkinter)",
    )
    p_gui.set_defaults(handler=_cmd_gui)

    return p


def main(argv: list[str] | None = None) -> int:
    """Точка входа CLI."""
    from lang_learn.config.dotenv_load import load_dotenv_files

    load_dotenv_files()

    if argv is None:
        argv_list = sys.argv[1:]
    else:
        argv_list = list(argv)

    parser = build_parser()
    if not argv_list:
        # По умолчанию — графический режим для учеников с нуля (A0 / Pre-A0).
        return _cmd_gui(argparse.Namespace())

    args = parser.parse_args(argv_list)
    handler = getattr(args, "handler", None)
    if handler is None:
        parser.print_help()
        return 0
    run = cast(Callable[[argparse.Namespace], int], handler)
    return run(args)


if __name__ == "__main__":
    raise SystemExit(main())
