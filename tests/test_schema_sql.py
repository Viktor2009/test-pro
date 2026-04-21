"""DDL из `db/schema.sql` применяется к in-memory SQLite без ошибок."""

import sqlite3
from pathlib import Path


def test_schema_sql_executes_on_sqlite() -> None:
    root = Path(__file__).resolve().parents[1]
    sql_path = root / "db" / "schema.sql"
    script = sql_path.read_text(encoding="utf-8")
    con = sqlite3.connect(":memory:")
    try:
        con.executescript(script)
        cur = con.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        names = {row[0] for row in cur.fetchall()}
    finally:
        con.close()
    assert "users" in names
    assert "attempts" in names
    assert "user_aliases" in names
