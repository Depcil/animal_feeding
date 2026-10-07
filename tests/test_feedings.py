from models import Animal, Feeding, User
from models.feedings import (
    cancel_feeding,
    create_feeding,
    get_feeding_status,
    get_remaining_norm,
    is_feeding_allowed,
)

DAY = "2026-10-07"


def setup_objects():
    return (
        Animal(1, "Барсик", "кот", 200),
        User(1, "Анна", "anna@example.com"),
        User(2, "Иван", "ivan@example.com"),
    )


def test_feeding_creation():
    animal, user, _ = setup_objects()
    feeding = Feeding(1, animal, DAY, user, "корм", 100)
    assert feeding.animal is animal
    assert feeding.user is user
    assert feeding.feeding_date == DAY
    assert not feeding.is_cancelled


def test_feeding_cancel_and_str():
    animal, user, _ = setup_objects()
    feeding = Feeding(1, animal, DAY, user, "корм", 100)
    assert "активно" in str(feeding)
    feeding.cancel()
    assert feeding.is_cancelled
    assert "отменено" in str(feeding)


def test_overfeeding_forbidden():
    animal, user, other = setup_objects()
    feedings = []
    first = create_feeding(feedings, animal, user, DAY, "корм", 150)
    second = create_feeding(feedings, animal, other, DAY, "корм", 100)
    assert first is not None
    assert second is None
    assert len(feedings) == 1
    assert get_remaining_norm(feedings, animal, DAY) == 50


def test_cancelled_feeding_does_not_count():
    animal, user, other = setup_objects()
    feedings = []
    first = create_feeding(feedings, animal, user, DAY, "корм", 200)
    first.cancel()
    assert is_feeding_allowed(feedings, animal, DAY, 200)
    again = create_feeding(feedings, animal, other, DAY, "корм", 200)
    assert again is not None
    assert len(feedings) == 2


def test_cancel_feeding_keeps_object():
    animal, user, _ = setup_objects()
    feedings = []
    create_feeding(feedings, animal, user, DAY, "корм", 100)
    assert cancel_feeding(feedings, 1)
    assert len(feedings) == 1
    assert feedings[0].is_cancelled
    assert not cancel_feeding(feedings, 1)


def test_status_text():
    assert get_feeding_status(True) == "Кормление разрешено"
    assert get_feeding_status(False) == "Суточная норма будет превышена"
