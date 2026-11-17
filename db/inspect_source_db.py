"""Просмотр структуры исходной базы ПР7 перед переносом в Django ORM.

Запуск из корня проекта: python db/inspect_source_db.py
Скрипт только читает базу и ничего в ней не меняет.
"""
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from db.database import get_db_path  # noqa: E402


def main():
    source_db = Path(get_db_path())
    if not source_db.exists():
        raise FileNotFoundError(f"Исходная база не найдена: {source_db}")

    with sqlite3.connect(source_db) as conn:
        conn.row_factory = sqlite3.Row
        tables = conn.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type = 'table' AND name NOT LIKE 'sqlite_%' "
            "ORDER BY name"
        ).fetchall()

        for (table,) in tables:
            print(f"\nТаблица: {table}")
            for column in conn.execute(f'PRAGMA table_info("{table}")'):
                print(
                    f"  {column['name']}: {column['type']}, "
                    f"NOT NULL={column['notnull']}, PK={column['pk']}"
                )
            count = conn.execute(f'SELECT COUNT(*) FROM "{table}"')
            print(f"  записей: {count.fetchone()[0]}")

        # Кормления должны ссылаться только на существующие записи.
        orphans = conn.execute(
            "SELECT COUNT(*) FROM feedings "
            "WHERE animal_id NOT IN (SELECT id FROM animals) "
            "   OR user_id NOT IN (SELECT id FROM users)"
        ).fetchone()[0]
        print(f"\nКормлений с несуществующими ссылками: {orphans}")


if __name__ == "__main__":
    main()
