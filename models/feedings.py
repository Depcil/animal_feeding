"""Класс Feeding и функции работы с кормлениями."""
from typing import List, Optional

from .animals import Animal
from .users import User


class Feeding:
    """Кормление животного сотрудником."""

    def __init__(
        self,
        feeding_id: int,
        animal: Animal,
        feeding_date: str,
        user: User,
        food: str,
        amount: int,
    ) -> None:
        """Создать объект кормления."""
        self.id = feeding_id
        self.animal = animal
        self.feeding_date = feeding_date
        self.user = user
        self.food = food
        self.amount = amount
        self.is_cancelled = False

    def cancel(self) -> None:
        """Отменить кормление (запись остается в коллекции)."""
        self.is_cancelled = True

    def __str__(self) -> str:
        """Строковое представление кормления."""
        state = "отменено" if self.is_cancelled else "активно"
        return (
            f"{self.animal.name}: {self.feeding_date}, {self.food}, "
            f"{self.amount} г, {self.user.name} [{state}]"
        )


def get_fed_amount(
    feedings: List[Feeding],
    animal: Animal,
    feeding_date: str,
) -> int:
    """Сумма активных кормлений животного за дату, г."""
    return sum(
        f.amount for f in feedings
        if f.animal.id == animal.id
        and f.feeding_date == feeding_date
        and not f.is_cancelled
    )


def get_remaining_norm(
    feedings: List[Feeding],
    animal: Animal,
    feeding_date: str,
) -> int:
    """Остаток суточной нормы животного на дату, г."""
    fed = get_fed_amount(feedings, animal, feeding_date)
    return max(animal.daily_norm - fed, 0)


def is_feeding_allowed(
    feedings: List[Feeding],
    animal: Animal,
    feeding_date: str,
    amount: int,
) -> bool:
    """Проверить, что порция не превысит суточную норму за дату."""
    return amount <= get_remaining_norm(feedings, animal, feeding_date)


def create_feeding(
    feedings: List[Feeding],
    animal: Animal,
    user: User,
    feeding_date: str,
    food: str,
    amount: int,
) -> Optional[Feeding]:
    """Создать Feeding; None, если суточная норма будет превышена."""
    if not is_feeding_allowed(feedings, animal, feeding_date, amount):
        return None
    feeding_id = max((f.id for f in feedings), default=0) + 1
    feeding = Feeding(feeding_id, animal, feeding_date, user, food, amount)
    feedings.append(feeding)
    return feeding


def cancel_feeding(feedings: List[Feeding], feeding_id: int) -> bool:
    """Найти кормление и вызвать его метод cancel()."""
    for feeding in feedings:
        if feeding.id == feeding_id and not feeding.is_cancelled:
            feeding.cancel()
            return True
    return False


def get_feeding_status(is_allowed: bool) -> str:
    """Вернуть текстовый статус кормления."""
    if is_allowed:
        return "Кормление разрешено"
    return "Суточная норма будет превышена"


def show_feedings(feedings: List[Feeding]) -> None:
    """Вывести информацию об объектах Feeding."""
    if not feedings:
        print("Кормлений нет.")
    for feeding in feedings:
        print(f"{feeding.id}. {feeding}")
