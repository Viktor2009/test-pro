"""SQLite-реализация ``ProgressRepository`` по ``db/schema.sql``."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, cast

from lang_learn.contracts.progress import ProgressRepository
from lang_learn.schemas.common import EntityId
from lang_learn.schemas.learning import AttemptRecord, LearningProfile


def _optional_int(value: object) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    return None


def _parse_created_at(raw: object) -> datetime | None:
    if raw is None:
        return None
    text = str(raw).strip()
    if not text:
        return None
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    return datetime.fromisoformat(text)


class SqliteProgressRepository(ProgressRepository):
    """
    Хранилище прогресса на одном соединении SQLite.

    Схема должна содержать ``user_aliases`` (внешний ``EntityId`` → ``users.id``).
    """

    def __init__(
        self,
        database: Path | str,
        *,
        schema_sql: str | None = None,
        schema_path: Path | None = None,
    ) -> None:
        script = schema_sql
        if script is None:
            if schema_path is None:
                msg = "Укажите schema_sql или schema_path"
                raise ValueError(msg)
            script = schema_path.read_text(encoding="utf-8")
        self._conn = sqlite3.connect(str(database))
        self._conn.row_factory = sqlite3.Row
        self._conn.executescript(script)

    def close(self) -> None:
        """Закрыть соединение с SQLite."""
        self._conn.close()

    def _ensure_user_id(self, external_id: str) -> int:
        cur = self._conn.execute(
            "SELECT user_id FROM user_aliases WHERE external_id = ?",
            (external_id,),
        )
        row = cur.fetchone()
        if row is not None:
            return int(cast(Any, row[0]))
        cur = self._conn.execute(
            "INSERT INTO users (display_name) VALUES (?)",
            (external_id,),
        )
        lid = cur.lastrowid
        if lid is None:
            msg = "SQLite: не удалось получить id после INSERT INTO users"
            raise RuntimeError(msg)
        uid = int(lid)
        self._conn.execute(
            "INSERT INTO user_aliases (external_id, user_id) VALUES (?, ?)",
            (external_id, uid),
        )
        return uid

    def load_profile(self, user_id: EntityId) -> LearningProfile | None:
        cur = self._conn.execute(
            """
            SELECT lp.interface_language, lp.target_language, lp.level_hint
            FROM learning_profiles lp
            JOIN user_aliases ua ON ua.user_id = lp.user_id
            WHERE ua.external_id = ?
            """,
            (user_id,),
        )
        row = cur.fetchone()
        if row is None:
            return None
        iface = cast(Any, row[0])
        return LearningProfile(
            user_id=user_id,
            interface_language=iface,
            target_language=cast(Any, row[1]),
            level_hint=cast(Any, row[2]),
        )

    def save_profile(self, profile: LearningProfile) -> None:
        with self._conn:
            uid = self._ensure_user_id(profile.user_id)
            self._conn.execute(
                """
                INSERT INTO learning_profiles
                    (user_id, interface_language, target_language, level_hint)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    interface_language = excluded.interface_language,
                    target_language = excluded.target_language,
                    level_hint = excluded.level_hint,
                    updated_utc = strftime('%Y-%m-%dT%H:%M:%fZ', 'now')
                """,
                (
                    uid,
                    profile.interface_language,
                    profile.target_language,
                    profile.level_hint,
                ),
            )

    def save_attempt(self, attempt: AttemptRecord) -> None:
        details_copy = dict(attempt.details)
        errors_raw = details_copy.pop("errors", [])
        if not isinstance(errors_raw, list):
            errors_raw = []
        errors_json = json.dumps(errors_raw, ensure_ascii=False)
        details_json = json.dumps(details_copy, ensure_ascii=False)
        lesson_id = _optional_int(details_copy.get("lesson_id"))
        scenario_id = _optional_int(details_copy.get("scenario_id"))
        target_skill = details_copy.get("skill_axis")
        target_skill_s = str(target_skill) if target_skill is not None else None
        ref_text = details_copy.get("reference_text")
        ref_text_s = str(ref_text) if ref_text is not None else None
        rec_next = details_copy.get("recommendation_next")
        rec_next_s = str(rec_next) if rec_next is not None else None
        with self._conn:
            uid = self._ensure_user_id(attempt.user_id)
            self._conn.execute(
                """
                INSERT INTO attempts (
                    user_id, lesson_id, scenario_id, exercise_id,
                    target_skill, reference_text, stt_transcript,
                    errors_json, score, recommendation_next, details_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    uid,
                    lesson_id,
                    scenario_id,
                    attempt.exercise_id,
                    target_skill_s,
                    ref_text_s,
                    attempt.transcript,
                    errors_json,
                    attempt.score,
                    rec_next_s,
                    details_json,
                ),
            )

    def list_attempts(
        self,
        user_id: EntityId,
        *,
        limit: int = 200,
    ) -> tuple[AttemptRecord, ...]:
        if limit <= 0:
            return ()
        cur = self._conn.execute(
            """
            SELECT a.id, a.exercise_id, a.stt_transcript, a.score, a.created_utc,
                   a.errors_json, a.details_json, a.reference_text,
                   a.recommendation_next, a.target_skill
            FROM attempts a
            JOIN user_aliases ua ON ua.user_id = a.user_id
            WHERE ua.external_id = ?
            ORDER BY a.id DESC
            LIMIT ?
            """,
            (user_id, limit),
        )
        rows = cur.fetchall()
        out: list[AttemptRecord] = []
        for row in rows:
            rid = int(cast(Any, row["id"]))
            details = json.loads(str(row["details_json"] or "{}"))
            errs = json.loads(str(row["errors_json"] or "[]"))
            if errs:
                details = {**details, "errors": errs}
            ref_text = row["reference_text"]
            if ref_text is not None:
                details = {**details, "reference_text": str(ref_text)}
            rec_next = row["recommendation_next"]
            if rec_next is not None:
                details = {**details, "recommendation_next": str(rec_next)}
            skill = row["target_skill"]
            if skill is not None:
                details = {**details, "skill_axis": str(skill)}
            out.append(
                AttemptRecord(
                    attempt_id=f"att-{rid}",
                    user_id=user_id,
                    exercise_id=str(row["exercise_id"]),
                    transcript=cast(Any, row["stt_transcript"]),
                    score=cast(Any, row["score"]),
                    created_at=_parse_created_at(row["created_utc"]),
                    details=details,
                ),
            )
        return tuple(out)

    def enqueue_review(
        self,
        user_id: EntityId,
        *,
        due_utc: str,
        item_kind: str,
        item_ref: str,
        payload: dict[str, object],
    ) -> None:
        payload_json = json.dumps(payload, ensure_ascii=False)
        with self._conn:
            uid = self._ensure_user_id(user_id)
            self._conn.execute(
                """
                INSERT INTO review_queue
                    (user_id, due_utc, item_kind, item_ref, payload_json)
                VALUES (?, ?, ?, ?, ?)
                """,
                (uid, due_utc, item_kind, item_ref, payload_json),
            )
