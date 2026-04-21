-- Схема SQLite: прогресс и контент (этап 0).
-- Кодировка текста: UTF-8. Время: UTC в TEXT (ISO 8601).

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_utc TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    display_name TEXT
);

CREATE TABLE IF NOT EXISTS learning_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE REFERENCES users (id) ON DELETE CASCADE,
    interface_language TEXT,
    target_language TEXT NOT NULL,
    level_hint TEXT,
    updated_utc TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

CREATE TABLE IF NOT EXISTS scenarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    description TEXT,
    theme TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS lessons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scenario_id INTEGER REFERENCES scenarios (id) ON DELETE SET NULL,
    title TEXT NOT NULL,
    sort_order INTEGER NOT NULL DEFAULT 0,
    metadata_json TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    lesson_id INTEGER REFERENCES lessons (id) ON DELETE SET NULL,
    scenario_id INTEGER REFERENCES scenarios (id) ON DELETE SET NULL,
    exercise_id TEXT NOT NULL,
    target_skill TEXT,
    reference_text TEXT,
    stt_transcript TEXT,
    errors_json TEXT NOT NULL DEFAULT '[]',
    score REAL,
    recommendation_next TEXT,
    created_utc TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    details_json TEXT NOT NULL DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_attempts_user_created
ON attempts (user_id, created_utc);

CREATE TABLE IF NOT EXISTS pronunciation_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    attempt_id INTEGER NOT NULL REFERENCES attempts (id) ON DELETE CASCADE,
    report_json TEXT NOT NULL,
    created_utc TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

CREATE TABLE IF NOT EXISTS review_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    due_utc TEXT NOT NULL,
    item_kind TEXT NOT NULL,
    item_ref TEXT NOT NULL,
    payload_json TEXT NOT NULL DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_review_queue_user_due
ON review_queue (user_id, due_utc);

CREATE TABLE IF NOT EXISTS session_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    started_utc TEXT NOT NULL,
    ended_utc TEXT,
    metadata_json TEXT NOT NULL DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_session_logs_user_started
ON session_logs (user_id, started_utc);

-- Сопоставление внешнего user id (EntityId) с INTEGER users.id (этап 6).
CREATE TABLE IF NOT EXISTS user_aliases (
    external_id TEXT PRIMARY KEY COLLATE NOCASE,
    user_id INTEGER NOT NULL REFERENCES users (id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_user_aliases_user
ON user_aliases (user_id);
