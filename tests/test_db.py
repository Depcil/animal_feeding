"""Исходная база ПР7 (sqlite3): структура, импорт из JSON и sql/queries.sql."""
import json
import re
import sqlite3

import pytest

from db.database import BASE_DIR, get_connection

QUERIES_FILE = BASE_DIR / "sql" / "queries.sql"


def json_count(name):
    with open(BASE_DIR / "data" / name, encoding="utf-8") as file:
        return len(json.load(file))


def test_tables_and_foreign_keys():
    conn = get_connection()
    tables = {
        row[0] for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        )
    }
    fks = {
        row[2] for row in conn.execute("PRAGMA foreign_key_list(feedings)")
    }
    conn.close()
    assert {"animals", "users", "feedings"} <= tables
    assert fks == {"animals", "users"}


def test_import_counts_match_json():
    conn = get_connection()
    for sql, name in (
        ("SELECT COUNT(*) FROM animals", "animals.json"),
        ("SELECT COUNT(*) FROM users", "users.json"),
        ("SELECT COUNT(*) FROM feedings", "feedings.json"),
    ):
        assert conn.execute(sql).fetchone()[0] == json_count(name)
    conn.close()


def test_foreign_key_is_checked():
    conn = get_connection()
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO feedings (animal_id, user_id, feeding_date, food, "
            "amount) VALUES (?, ?, ?, ?, ?)",
            (999, 1, "2026-10-07", "корм", 10),
        )
    conn.rollback()
    conn.close()


def split_queries():
    text = QUERIES_FILE.read_text(encoding="utf-8")
    lines = [
        line for line in text.splitlines()
        if not line.startswith(".") and not line.strip().startswith("--")
    ]
    return [q.strip() for q in "\n".join(lines).split(";") if q.strip()]


def test_queries_file_runs_and_covers_kinds():
    queries = split_queries()
    assert len(queries) >= 10
    conn = get_connection()
    for query in queries:
        conn.execute(query).fetchall()
    conn.close()
    upper = [q.upper() for q in queries]

    def count(pattern):
        return sum(1 for q in upper if re.search(pattern, q))

    assert count(r"\bWHERE\b") >= 2
    assert count(r"\bJOIN\b") >= 2
    assert count(r"\b(COUNT|SUM|MIN|MAX|AVG)\(") >= 2
    assert count(r"\bGROUP BY\b") >= 2
    assert count(r"\bHAVING\b") >= 1
