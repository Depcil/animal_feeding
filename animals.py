"""Функции работы с животными (данные – словари)."""
from utils import next_id


def add_animal(
    animals: dict[int, dict],
    name: str,
    species: str,
    daily_norm: int,
) -> dict:
    """Добавить животное в словарь animals и вернуть его данные."""
    animal_id = next_id(list(animals))
    animal = {
        "id": animal_id,
        "name": name,
        "species": species,
        "daily_norm": daily_norm,
    }
    animals[animal_id] = animal
    return animal


def find_animal(animals: dict[int, dict], query: str) -> list[dict]:
    """Найти животных по подстроке клички или вида."""
    query = query.lower()
    return [
        animal for animal in animals.values()
        if query in animal["name"].lower()
        or query in animal["species"].lower()
    ]


def check_animal_norm(
    animals: dict[int, dict],
    animal_id: int,
    amount: int,
) -> bool:
    """Проверить, что порция не больше суточной нормы животного."""
    animal = animals.get(animal_id)
    if animal is None:
        return False
    return amount <= animal["daily_norm"]


def filter_animals_by_norm(
    animals: dict[int, dict],
    min_norm: int,
) -> list[dict]:
    """Отобрать животных с суточной нормой не меньше min_norm."""
    return [
        animal for animal in animals.values()
        if animal["daily_norm"] >= min_norm
    ]


def sort_animals(animals: dict[int, dict]) -> list[dict]:
    """Отсортировать животных по суточной норме."""
    return sorted(animals.values(), key=lambda a: a["daily_norm"])
