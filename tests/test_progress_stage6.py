"""Этап 6: KPI, компетенции, SQLite-прогресс."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from lang_learn.learning.progress_report import compute_progress_overview
from lang_learn.learning.srs_planner import plan_review_items, weak_skill_axes
from lang_learn.persistence.sqlite_progress import SqliteProgressRepository
from lang_learn.schemas.learning import AttemptRecord, LearningProfile


def test_compute_progress_overview_empty() -> None:
    overview = compute_progress_overview(())
    assert overview.kpis.pronunciation_score == 0.0
    assert overview.travel.percent == 0.0
    assert overview.competency.pronunciation == 0.0


def test_compute_progress_overview_with_travel_scores() -> None:
    attempts = (
        AttemptRecord(
            attempt_id="1",
            user_id="u",
            exercise_id="e1",
            score=0.8,
            details={"scenario_slug": "airport", "skill_axis": "dialog_scenario"},
        ),
        AttemptRecord(
            attempt_id="2",
            user_id="u",
            exercise_id="e2",
            score=0.6,
            details={"scenario_slug": "hotel", "skill_axis": "lexicon"},
        ),
    )
    overview = compute_progress_overview(attempts)
    assert overview.travel.percent > 0.0
    assert "airport" in overview.travel.by_scenario


def test_weak_skill_axes_and_plan() -> None:
    from lang_learn.schemas.progress_analytics import CompetencySnapshot

    snap = CompetencySnapshot(
        lexicon=0.4,
        comprehension=0.9,
        pronunciation=0.5,
        dialog_scenario=0.8,
    )
    weak = weak_skill_axes(snap, threshold=0.55)
    assert "lexicon" in weak
    assert "pronunciation" in weak
    plan = plan_review_items(weak, base_hours=12)
    assert len(plan) == len(weak)
    assert all(len(t) == 3 for t in plan)


def test_sqlite_progress_repository_roundtrip(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    schema_sql = (root / "db" / "schema.sql").read_text(encoding="utf-8")
    db_path = tmp_path / "p.sqlite"
    repo = SqliteProgressRepository(db_path, schema_sql=schema_sql)
    try:
        prof = LearningProfile(
            user_id="ext-1",
            interface_language="ru-RU",
            target_language="en-US",
            level_hint="a1",
        )
        repo.save_profile(prof)
        loaded = repo.load_profile("ext-1")
        assert loaded is not None
        assert loaded.target_language == "en-US"
        repo.save_attempt(
            AttemptRecord(
                attempt_id="x1",
                user_id="ext-1",
                exercise_id="ex-1",
                transcript="hi",
                score=0.7,
                details={"scenario_slug": "shop", "skill_axis": "pronunciation"},
            ),
        )
        listed = repo.list_attempts("ext-1", limit=10)
        assert len(listed) == 1
        assert listed[0].exercise_id == "ex-1"
        assert listed[0].attempt_id.startswith("att-")
        repo.enqueue_review(
            "ext-1",
            due_utc="2099-01-01T00:00:00Z",
            item_kind="skill_axis",
            item_ref="lexicon",
            payload={"note": "review"},
        )
    finally:
        repo.close()
    con = sqlite3.connect(str(db_path))
    try:
        n = con.execute("SELECT COUNT(*) FROM review_queue").fetchone()[0]
        assert int(n) == 1
        raw = con.execute(
            "SELECT payload_json FROM review_queue LIMIT 1",
        ).fetchone()
        assert raw is not None
        data = json.loads(str(raw[0]))
        assert data["note"] == "review"
    finally:
        con.close()
