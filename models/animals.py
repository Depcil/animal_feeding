"""Класс Animal и функции работы с коллекцией животных."""
from typing import List, Optional


class Animal:
    """Животное, за кормлением которого ведется учет."""

    def __init__(
        self,
        animal_id: int,
        name: str,
        species: str,
        daily_norm: int,
    ) -> None:
        """Создать объект животного."""
        self.id = animal_id
        self.name = name
        self.species = species
        self.daily_norm = daily_norm

    def fits_daily_norm(self, amount: int) -> bool:
        """Проверить, что порция не больше суточной нормы."""
        return amount <= self.daily_norm

    @staticmethod
    def validate_norm(daily_norm: int) -> bool:
        """Проверить корректность суточной нормы."""
        return daily_norm > 0

    @property
    def info(self) -> str:
        """Краткое описание животного для отображения."""
        return f"{self.name} ({self.species})"

    def __str__(self) -> str:
        """Строковое представление животного."""
        return f"{self.info}, норма {self.daily_norm} г/сутки"


def add_animal(
    animals: List[Animal],
    name: str,
    species: str,
    daily_norm: int,
) -> Animal:
    """Создать объект Animal, добавить в коллекцию и вернуть его."""
    animal_id = max((a.id for a in animals), default=0) + 1
    animal = Animal(animal_id, name, species, daily_norm)
    animals.append(animal)
    return animal


def find_animal(animals: List[Animal], query: str) -> List[Animal]:
    """Найти животных по подстроке клички или вида."""
    query = query.lower()
    return [
        a for a in animals
        if query in a.name.lower() or query in a.species.lower()
    ]


def find_animal_by_id(
    animals: List[Animal],
    animal_id: int,
) -> Optional[Animal]:
    """Найти животное по идентификатору."""
    for animal in animals:
        if animal.id == animal_id:
            return animal
    return None


def check_animal_norm(
    animals: List[Animal],
    animal_id: int,
    amount: int,
) -> bool:
    """Найти животное и проверить, укладывается ли порция в норму."""
    animal = find_animal_by_id(animals, animal_id)
    return animal is not None and animal.fits_daily_norm(amount)


def filter_animals_by_norm(
    animals: List[Animal],
    min_norm: int,
) -> List[Animal]:
    """Отобрать животных с суточной нормой не меньше min_norm."""
    return [a for a in animals if a.daily_norm >= min_norm]


def sort_animals(animals: List[Animal]) -> List[Animal]:
    """Отсортировать животных по суточной норме."""
    return sorted(animals, key=lambda a: a.daily_norm)


def show_animals(animals: List[Animal]) -> None:
    """Вывести информацию об объектах Animal."""
    if not animals:
        print("Животные не найдены.")
    for animal in animals:
        print(f"{animal.id}. {animal}")
