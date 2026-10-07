"""Загрузка и сохранение объектов в JSON-файлах."""
import json
from typing import List

from models import Animal, Feeding, User
from models.animals import find_animal_by_id
from models.users import find_user_by_id


def _load_list(filename: str) -> List[dict]:
    """Прочитать список записей из JSON-файла."""
    try:
        with open(filename, encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Файл {filename} не найден, данные пусты.")
    except json.JSONDecodeError:
        print(f"Файл {filename} содержит некорректный JSON.")
    return []


def _save_list(filename: str, items: List[dict]) -> None:
    """Записать список записей в JSON-файл."""
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(items, file, ensure_ascii=False, indent=4)


def load_animals(filename: str) -> List[Animal]:
    """JSON -> объекты Animal."""
    return [
        Animal(d["id"], d["name"], d["species"], d["daily_norm"])
        for d in _load_list(filename)
    ]


def save_animals(filename: str, animals: List[Animal]) -> None:
    """Объекты Animal -> JSON."""
    _save_list(filename, [
        {
            "id": a.id,
            "name": a.name,
            "species": a.species,
            "daily_norm": a.daily_norm,
        }
        for a in animals
    ])


def load_users(filename: str) -> List[User]:
    """JSON -> объекты User."""
    return [User.from_data(d) for d in _load_list(filename)]


def save_users(filename: str, users: List[User]) -> None:
    """Объекты User -> JSON."""
    _save_list(filename, [
        {"id": u.id, "name": u.name, "email": u.email} for u in users
    ])


def load_feedings(
    filename: str,
    animals: List[Animal],
    users: List[User],
) -> List[Feeding]:
    """JSON -> объекты Feeding со связями на Animal и User."""
    feedings: List[Feeding] = []
    for d in _load_list(filename):
        animal = find_animal_by_id(animals, d["animal_id"])
        user = find_user_by_id(users, d["user_id"])
        if animal is None or user is None:
            print(f"Кормление {d['id']} пропущено: нет животного/сотрудника.")
            continue
        feeding = Feeding(
            d["id"], animal, d["feeding_date"], user, d["food"], d["amount"]
        )
        feeding.is_cancelled = d["is_cancelled"]
        feedings.append(feeding)
    return feedings


def save_feedings(filename: str, feedings: List[Feeding]) -> None:
    """Объекты Feeding -> JSON (вместо объектов – идентификаторы)."""
    _save_list(filename, [
        {
            "id": f.id,
            "animal_id": f.animal.id,
            "feeding_date": f.feeding_date,
            "user_id": f.user.id,
            "food": f.food,
            "amount": f.amount,
            "is_cancelled": f.is_cancelled,
        }
        for f in feedings
    ])
