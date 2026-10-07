"""Загрузка и сохранение данных в JSON-файлах."""
import json


def _load_list(filename: str) -> list[dict]:
    """Прочитать список записей из JSON-файла."""
    try:
        with open(filename, encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Файл {filename} не найден, данные пусты.")
    except json.JSONDecodeError:
        print(f"Файл {filename} содержит некорректный JSON.")
    return []


def _save_list(filename: str, items: list[dict]) -> None:
    """Записать список записей в JSON-файл."""
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(items, file, ensure_ascii=False, indent=4)


def load_animals(filename: str) -> dict[int, dict]:
    """Загрузить животных: ключ – идентификатор."""
    return {item["id"]: item for item in _load_list(filename)}


def save_animals(filename: str, animals: dict[int, dict]) -> None:
    """Сохранить животных в JSON."""
    _save_list(filename, list(animals.values()))


def load_feedings(filename: str) -> list[dict]:
    """Загрузить кормления."""
    return _load_list(filename)


def save_feedings(filename: str, feedings: list[dict]) -> None:
    """Сохранить кормления в JSON."""
    _save_list(filename, feedings)
