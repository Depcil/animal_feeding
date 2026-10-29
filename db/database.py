"""Подключение к базе данных SQLite проекта PetFeed."""
import os
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SCHEMA_FILE = BASE_DIR / "sql" / "schema.sql"

# Путь к базе можно переопределить переменной окружения PETFEED_DB
# (так тесты работают с временной копией базы, не трогая основную).
DB_PATH = os.environ.get(
    "PETFEED_DB",
    str(BASE_DIR / "data" / "petfeed.sqlite"),
)


def get_db_path():
    """Текущий путь к файлу базы данных."""
    return os.environ.get("PETFEED_DB", DB_PATH)


def get_connection():
    """Открыть соединение с SQLite и включить проверку внешних ключей."""
    conn = sqlite3.connect(get_db_path())
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def create_schema(conn):
    """Выполнить sql/schema.sql (CREATE TABLE IF NOT EXISTS ...)."""
    with open(SCHEMA_FILE, encoding="utf-8") as file:
        conn.executescript(file.read())
