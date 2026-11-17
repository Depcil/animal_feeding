"""Перенос данных из базы ПР7 (data/petfeed.sqlite) в таблицы Django.

Запуск из корня проекта после python manage.py migrate:
    python db/import_sqlite_to_orm.py

Исходная база только читается. Идентификаторы записей сохраняются,
поэтому связи кормлений с животными и сотрудниками не теряются.
Скрипт можно запускать повторно: записи обновляются, а не дублируются.
"""
import os
import sqlite3
import sys
from datetime import date
from pathlib import Path

import django

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "petfeed.settings")
django.setup()

from django.db import transaction  # noqa: E402

from animals.models import Animal  # noqa: E402
from db.database import get_db_path  # noqa: E402
from employees.models import Employee  # noqa: E402
from feedings.models import Feeding  # noqa: E402


def read_source(source_db):
    with sqlite3.connect(source_db) as conn:
        conn.row_factory = sqlite3.Row
        animals = conn.execute(
            "SELECT id, name, species, daily_norm FROM animals ORDER BY id"
        ).fetchall()
        users = conn.execute(
            "SELECT id, name, email FROM users ORDER BY id"
        ).fetchall()
        feedings = conn.execute(
            "SELECT id, animal_id, user_id, feeding_date, food, amount, "
            "is_cancelled, comment FROM feedings ORDER BY id"
        ).fetchall()
    return animals, users, feedings


def main():
    source_db = Path(get_db_path())
    if not source_db.exists():
        raise FileNotFoundError(f"Исходная база не найдена: {source_db}")

    animals, users, feedings = read_source(source_db)

    # Одна транзакция: при ошибке не останется наполовину перенесенных данных.
    with transaction.atomic():
        for row in animals:
            Animal.objects.update_or_create(
                pk=row["id"],
                defaults={
                    "name": row["name"],
                    "species": row["species"],
                    "daily_norm": row["daily_norm"],
                },
            )
        for row in users:
            Employee.objects.update_or_create(
                pk=row["id"],
                defaults={"name": row["name"], "email": row["email"]},
            )
        # Кормления переносятся последними: они ссылаются на обе таблицы.
        for row in feedings:
            Feeding.objects.update_or_create(
                pk=row["id"],
                defaults={
                    "animal_id": row["animal_id"],
                    "employee_id": row["user_id"],
                    "feeding_date": date.fromisoformat(row["feeding_date"]),
                    "food": row["food"],
                    "amount": row["amount"],
                    "is_cancelled": bool(row["is_cancelled"]),
                    "comment": row["comment"] or "",
                },
            )

    print(
        f"Перенесено: животных {Animal.objects.count()}, "
        f"сотрудников {Employee.objects.count()}, "
        f"кормлений {Feeding.objects.count()}"
    )


if __name__ == "__main__":
    main()
