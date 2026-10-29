import json
import re
import sqlite3

import pytest
from django.test import Client

from db.database import BASE_DIR, get_connection

client = Client()
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


def test_animals_page_from_db_and_search():
    text = client.get("/animals/").content.decode()
    assert "Всего животных: 4" in text
    found = client.get("/animals/", {"q": "Рекс"}).content.decode()
    assert "Всего животных: 1" in found and "Рекс" in found
    by_norm = client.get("/animals/", {"min_norm": "200"}).content.decode()
    assert "Всего животных: 2" in by_norm


def test_search_is_parameterized():
    text = client.get("/animals/", {"q": "' OR 1=1 --"}).content.decode()
    assert "Животные не найдены." in text


def test_available_animals_by_date():
    empty = client.get("/animals/available/").content.decode()
    assert "Дата: " not in empty
    text = client.get(
        "/animals/available/", {"date": "2026-10-07"}
    ).content.decode()
    assert "Рекс" in text and "Мурка" in text and "Кеша" in text
    assert "Барсик" not in text  # норма 200 г уже выдана
    bad = client.get("/animals/available/", {"date": "abc"}).content.decode()
    assert "Дата указана неверно" in bad


def test_animal_detail_by_date():
    text = client.get("/animals/1/", {"date": "2026-10-07"}).content.decode()
    assert "получил:</strong> 200 г" in text
    assert "норма выполнена" in text


def test_feedings_filter_and_pagination():
    active = client.get("/feedings/", {"status": "active"}).content.decode()
    assert "Всего записей: 8" in active and "Отменено" not in active
    page2 = client.get("/feedings/", {"page": "2"}).content.decode()
    assert "Страница 2 из 2" in page2


def test_statistics_page():
    response = client.get("/feedings/statistics/")
    text = response.content.decode()
    assert response.status_code == 200
    assert "Рекс" in text and "850" in text
    strict = client.get(
        "/feedings/statistics/", {"min_count": "3"}
    ).content.decode()
    assert "Рекс – 3" in strict and "Барсик – 2" not in strict


def test_navigation_has_statistics():
    text = client.get("/").content.decode()
    assert 'href="/feedings/statistics/"' in text
