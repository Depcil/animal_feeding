from datetime import date

from animals import add_animal
from feedings import (
    cancel_feeding,
    create_feeding,
    get_feeding_status,
    is_feeding_allowed,
)

DAY = date(2026, 10, 7)


def make_animals():
    animals = {}
    add_animal(animals, "Барсик", "кот", 200)
    return animals


def test_feeding_allowed_when_empty():
    assert is_feeding_allowed([], make_animals(), 1, DAY, 150)


def test_create_feeding_adds_record():
    feedings = []
    result = create_feeding(feedings, make_animals(), 1, DAY, "корм", 100)
    assert result is not None
    assert len(feedings) == 1


def test_overfeeding_forbidden():
    animals = make_animals()
    feedings = []
    create_feeding(feedings, animals, 1, DAY, "корм", 150)
    assert not is_feeding_allowed(feedings, animals, 1, DAY, 100)
    assert create_feeding(feedings, animals, 1, DAY, "корм", 100) is None


def test_other_day_not_affected():
    animals = make_animals()
    feedings = []
    create_feeding(feedings, animals, 1, DAY, "корм", 200)
    assert is_feeding_allowed(feedings, animals, 1, date(2026, 10, 8), 200)


def test_cancel_feeding_and_status():
    animals = make_animals()
    feedings = []
    create_feeding(feedings, animals, 1, DAY, "корм", 200)
    assert cancel_feeding(feedings, 1)
    assert not cancel_feeding(feedings, 1)
    assert get_feeding_status(True) == "Кормление разрешено"
