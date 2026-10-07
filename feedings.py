"""Функции работы с кормлениями (данные – словари)."""
from datetime import date
from typing import Optional

from utils import next_id


def get_fed_amount(
    feedings: list[dict],
    animal_id: int,
    feeding_date: date,
) -> int:
    """Вернуть, сколько грамм корма животное получило за дату."""
    day = feeding_date.isoformat()
    return sum(
        f["amount"] for f in feedings
        if f["animal_id"] == animal_id and f["feeding_date"] == day
    )


def is_feeding_allowed(
    feedings: list[dict],
    animals: dict[int, dict],
    animal_id: int,
    feeding_date: date,
    amount: int,
) -> bool:
    """Проверить, что порция не превысит суточную норму за дату."""
    animal = animals.get(animal_id)
    if animal is None:
        return False
    fed = get_fed_amount(feedings, animal_id, feeding_date)
    return fed + amount <= animal["daily_norm"]


def create_feeding(
    feedings: list[dict],
    animals: dict[int, dict],
    animal_id: int,
    feeding_date: date,
    food: str,
    amount: int,
) -> Optional[dict]:
    """Создать запись о кормлении; None, если норма будет превышена."""
    if not is_feeding_allowed(
        feedings, animals, animal_id, feeding_date, amount
    ):
        return None
    feeding = {
        "id": next_id([f["id"] for f in feedings]),
        "animal_id": animal_id,
        "feeding_date": feeding_date.isoformat(),
        "food": food,
        "amount": amount,
    }
    feedings.append(feeding)
    return feeding


def cancel_feeding(feedings: list[dict], feeding_id: int) -> bool:
    """Отменить кормление: удалить запись из списка."""
    for feeding in feedings:
        if feeding["id"] == feeding_id:
            feedings.remove(feeding)
            return True
    return False


def get_feeding_status(is_allowed: bool) -> str:
    """Вернуть текстовый статус кормления (функция из ПР1)."""
    if is_allowed:
        return "Кормление разрешено"
    return "Суточная норма будет превышена"
