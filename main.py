"""Консольное приложение учета кормления животных (ПР3, ООП)."""
from typing import List

from models import Animal, Feeding, User
from models.animals import (
    add_animal,
    check_animal_norm,
    filter_animals_by_norm,
    find_animal,
    find_animal_by_id,
    show_animals,
    sort_animals,
)
from models.feedings import (
    cancel_feeding,
    create_feeding,
    get_feeding_status,
    is_feeding_allowed,
    show_feedings,
)
from models.users import add_user, find_user, find_user_by_id, show_users
from storage import (
    load_animals,
    load_feedings,
    load_users,
    save_animals,
    save_feedings,
    save_users,
)
from utils import input_date, input_int

ANIMALS_FILE = "data/animals.json"
USERS_FILE = "data/users.json"
FEEDINGS_FILE = "data/feedings.json"

MENU = """
=== Сервис учета кормления животных ===
1. Показать животных
2. Найти животное по кличке или виду
3. Проверить порцию по суточной норме
4. Проверить возможность кормления на дату
5. Записать кормление
6. Отменить кормление
7. Показать кормления
8. Добавить животное
9. Показать животных по возрастанию нормы
10. Отобрать животных по норме
11. Показать сотрудников
12. Добавить сотрудника
13. Найти сотрудника
0. Выход
"""


def create_new_feeding(
    feedings: List[Feeding],
    animals: List[Animal],
    users: List[User],
) -> None:
    """Пользовательский сценарий записи кормления."""
    animal = find_animal_by_id(animals, input_int("ID животного: "))
    if animal is None:
        print("Животное не найдено.")
        return
    user = find_user_by_id(users, input_int("ID сотрудника: "))
    if user is None:
        print("Сотрудник не найден.")
        return
    day = input_date("Дата (ДД.ММ.ГГГГ): ").isoformat()
    food = input("Корм: ")
    amount = input_int("Порция, г: ")
    feeding = create_feeding(feedings, animal, user, day, food, amount)
    if feeding is None:
        print("Кормление не записано: суточная норма будет превышена.")
    else:
        print(f"Кормление записано, ID {feeding.id}.")


def check_feeding_on_date(
    feedings: List[Feeding],
    animals: List[Animal],
) -> None:
    """Проверить возможность кормления на дату."""
    animal = find_animal_by_id(animals, input_int("ID животного: "))
    if animal is None:
        print("Животное не найдено.")
        return
    day = input_date("Дата (ДД.ММ.ГГГГ): ").isoformat()
    amount = input_int("Порция, г: ")
    print(get_feeding_status(
        is_feeding_allowed(feedings, animal, day, amount)))


def add_new_animal(animals: List[Animal]) -> None:
    """Сценарий добавления животного."""
    name = input("Кличка: ")
    species = input("Вид: ")
    norm = input_int("Суточная норма, г: ")
    if not Animal.validate_norm(norm):
        print("Норма должна быть положительной.")
        return
    add_animal(animals, name, species, norm)
    print("Животное добавлено.")


def main() -> None:
    """Точка запуска: загрузка данных, меню, сохранение."""
    animals = load_animals(ANIMALS_FILE)
    users = load_users(USERS_FILE)
    feedings = load_feedings(FEEDINGS_FILE, animals, users)
    while True:
        print(MENU)
        choice = input("Выберите действие: ").strip()
        if choice == "0":
            break
        elif choice == "1":
            show_animals(animals)
        elif choice == "2":
            show_animals(find_animal(animals, input("Кличка или вид: ")))
        elif choice == "3":
            animal_id = input_int("ID животного: ")
            amount = input_int("Порция, г: ")
            ok = check_animal_norm(animals, animal_id, amount)
            print("Порция укладывается в норму" if ok
                  else "Порция больше суточной нормы или животного нет")
        elif choice == "4":
            check_feeding_on_date(feedings, animals)
        elif choice == "5":
            create_new_feeding(feedings, animals, users)
        elif choice == "6":
            done = cancel_feeding(feedings, input_int("ID кормления: "))
            print("Кормление отменено." if done
                  else "Активное кормление не найдено.")
        elif choice == "7":
            show_feedings(feedings)
        elif choice == "8":
            add_new_animal(animals)
        elif choice == "9":
            show_animals(sort_animals(animals))
        elif choice == "10":
            show_animals(filter_animals_by_norm(
                animals, input_int("Минимальная норма, г: ")))
        elif choice == "11":
            show_users(users)
        elif choice == "12":
            add_user(users, input("Имя: "), input("Email: "))
        elif choice == "13":
            show_users(find_user(users, input("Имя или email: ")))
        else:
            print("Неизвестный пункт меню.")
    save_animals(ANIMALS_FILE, animals)
    save_users(USERS_FILE, users)
    save_feedings(FEEDINGS_FILE, feedings)


if __name__ == "__main__":
    main()
