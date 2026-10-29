"""Перенос данных PetFeed из JSON-файлов в базу SQLite.

Запуск из корня проекта: python -m db.import_json
Скрипт можно запускать повторно: таблицы очищаются и заполняются заново.
"""
import json

from db.database import BASE_DIR, create_schema, get_connection

ANIMALS_FILE = BASE_DIR / "data" / "animals.json"
USERS_FILE = BASE_DIR / "data" / "users.json"
FEEDINGS_FILE = BASE_DIR / "data" / "feedings.json"


def load_json(filename):
    """Прочитать список записей из JSON-файла."""
    with open(filename, encoding="utf-8") as file:
        return json.load(file)


def clear_tables(conn):
    """Удалить старые записи: сначала зависимую таблицу, затем справочники."""
    conn.execute("DELETE FROM feedings")
    conn.execute("DELETE FROM users")
    conn.execute("DELETE FROM animals")


def import_animals(conn, filename=ANIMALS_FILE):
    animals = load_json(filename)
    conn.executemany(
        """
        INSERT INTO animals (id, name, species, daily_norm)
        VALUES (?, ?, ?, ?)
        """,
        [
            (a["id"], a["name"], a["species"], a["daily_norm"])
            for a in animals
        ],
    )
    return len(animals)


def import_users(conn, filename=USERS_FILE):
    users = load_json(filename)
    conn.executemany(
        """
        INSERT INTO users (id, name, email)
        VALUES (?, ?, ?)
        """,
        [(u["id"], u["name"], u["email"]) for u in users],
    )
    return len(users)


def import_feedings(conn, filename=FEEDINGS_FILE):
    feedings = load_json(filename)
    conn.executemany(
        """
        INSERT INTO feedings (
            id, animal_id, user_id, feeding_date,
            food, amount, is_cancelled, comment
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                f["id"],
                f["animal_id"],
                f["user_id"],
                f["feeding_date"],
                f["food"],
                f["amount"],
                int(f["is_cancelled"]),
                f.get("comment"),
            )
            for f in feedings
        ],
    )
    return len(feedings)


def main():
    conn = get_connection()
    try:
        create_schema(conn)
        clear_tables(conn)
        # Порядок важен: feedings ссылается на animals и users.
        counts = (
            import_animals(conn),
            import_users(conn),
            import_feedings(conn),
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
    print(
        "Импортировано: животных – {}, сотрудников – {}, "
        "кормлений – {}".format(*counts)
    )


if __name__ == "__main__":
    main()
