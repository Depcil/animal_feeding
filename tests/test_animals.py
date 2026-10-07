from models import Animal
from models.animals import (
    add_animal,
    check_animal_norm,
    filter_animals_by_norm,
    find_animal,
    find_animal_by_id,
    sort_animals,
)


def make_animals():
    return [Animal(1, "Барсик", "кот", 200), Animal(2, "Рекс", "собака", 600)]


def test_animal_creation():
    animal = Animal(1, "Барсик", "кот", 200)
    assert animal.id == 1
    assert animal.name == "Барсик"
    assert animal.species == "кот"
    assert animal.daily_norm == 200


def test_animal_fits_daily_norm():
    animal = Animal(1, "Барсик", "кот", 200)
    assert animal.fits_daily_norm(150)
    assert not animal.fits_daily_norm(250)


def test_animal_str_and_info():
    animal = Animal(1, "Барсик", "кот", 200)
    assert animal.info == "Барсик (кот)"
    assert str(animal) == "Барсик (кот), норма 200 г/сутки"


def test_validate_norm():
    assert Animal.validate_norm(100)
    assert not Animal.validate_norm(0)


def test_add_animal_returns_object():
    animals = []
    animal = add_animal(animals, "Мурка", "кошка", 180)
    assert animals == [animal]
    assert animal.id == 1


def test_find_and_check():
    animals = make_animals()
    assert len(find_animal(animals, "СОБАК")) == 1
    assert find_animal_by_id(animals, 2).name == "Рекс"
    assert find_animal_by_id(animals, 99) is None
    assert check_animal_norm(animals, 1, 150)
    assert not check_animal_norm(animals, 1, 250)


def test_filter_and_sort():
    animals = make_animals()
    assert [a.name for a in filter_animals_by_norm(animals, 300)] == ["Рекс"]
    assert sort_animals(animals[::-1])[0].name == "Барсик"
