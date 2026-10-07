from animals import (
    add_animal,
    check_animal_norm,
    filter_animals_by_norm,
    find_animal,
    sort_animals,
)


def make_animals():
    animals = {}
    add_animal(animals, "Барсик", "кот", 200)
    add_animal(animals, "Рекс", "собака", 600)
    return animals


def test_add_animal():
    animals = {}
    add_animal(animals, "Барсик", "кот", 200)
    assert len(animals) == 1
    assert animals[1]["name"] == "Барсик"


def test_find_animal():
    assert len(find_animal(make_animals(), "СОБАК")) == 1


def test_check_animal_norm():
    animals = make_animals()
    assert check_animal_norm(animals, 1, 150)
    assert not check_animal_norm(animals, 1, 250)
    assert not check_animal_norm(animals, 99, 10)


def test_filter_animals_by_norm():
    result = filter_animals_by_norm(make_animals(), 300)
    assert [a["name"] for a in result] == ["Рекс"]


def test_sort_animals():
    result = sort_animals(make_animals())
    assert result[0]["daily_norm"] <= result[1]["daily_norm"]
