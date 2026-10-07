"""Консольное приложение учета кормления животных (ПР2)."""
from animals import (
    add_animal,
    check_animal_norm,
    filter_animals_by_norm,
    find_animal,
    sort_animals,
)
from feedings import (
    cancel_feeding,
    create_feeding,
    get_feeding_status,
    is_feeding_allowed,
)
from storage import (
    load_animals,
    load_feedings,
    save_animals,
    save_feedings,
)
from utils import input_date, input_int

ANIMALS_FILE = "data/animals.json"
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
0. Выход
"""


def show_animals(animals: list[dict]) -> None:
    """Вывести список животных."""
    if not animals:
        print("Животные не найдены.")
    for a in animals:
        print(f"{a['id']}. {a['name']} ({a['species']}), "
              f"норма {a['daily_norm']} г/сутки")


def show_feedings(feedings: list[dict], animals: dict[int, dict]) -> None:
    """Вывести список кормлений."""
    if not feedings:
        print("Кормлений нет.")
    for f in feedings:
        name = animals[f["animal_id"]]["name"]
        print(f"{f['id']}. {name}: {f['feeding_date']}, "
              f"{f['food']}, {f['amount']} г")


def main() -> None:
    """Точка запуска: цикл меню."""
    animals = load_animals(ANIMALS_FILE)
    feedings = load_feedings(FEEDINGS_FILE)
    while True:
        print(MENU)
        choice = input("Выберите действие: ").strip()
        if choice == "0":
            break
        elif choice == "1":
            show_animals(list(animals.values()))
        elif choice == "2":
            query = input("Кличка или вид: ")
            show_animals(find_animal(animals, query))
        elif choice == "3":
            animal_id = input_int("ID животного: ")
            amount = input_int("Порция, г: ")
            ok = check_animal_norm(animals, animal_id, amount)
            print("Порция укладывается в норму" if ok
                  else "Порция больше суточной нормы или животного нет")
        elif choice == "4":
            animal_id = input_int("ID животного: ")
            day = input_date("Дата (ДД.ММ.ГГГГ): ")
            amount = input_int("Порция, г: ")
            print(get_feeding_status(is_feeding_allowed(
                feedings, animals, animal_id, day, amount)))
        elif choice == "5":
            animal_id = input_int("ID животного: ")
            day = input_date("Дата (ДД.ММ.ГГГГ): ")
            food = input("Корм: ")
            amount = input_int("Порция, г: ")
            result = create_feeding(
                feedings, animals, animal_id, day, food, amount)
            if result is None:
                print("Кормление не записано: норма превышена.")
            else:
                save_feedings(FEEDINGS_FILE, feedings)
                print(f"Кормление записано, ID {result['id']}.")
        elif choice == "6":
            if cancel_feeding(feedings, input_int("ID кормления: ")):
                save_feedings(FEEDINGS_FILE, feedings)
                print("Кормление отменено.")
            else:
                print("Кормление не найдено.")
        elif choice == "7":
            show_feedings(feedings, animals)
        elif choice == "8":
            name = input("Кличка: ")
            species = input("Вид: ")
            norm = input_int("Суточная норма, г: ")
            add_animal(animals, name, species, norm)
            save_animals(ANIMALS_FILE, animals)
            print("Животное добавлено.")
        elif choice == "9":
            show_animals(sort_animals(animals))
        elif choice == "10":
            show_animals(filter_animals_by_norm(
                animals, input_int("Минимальная норма, г: ")))
        else:
            print("Неизвестный пункт меню.")
    save_animals(ANIMALS_FILE, animals)
    save_feedings(FEEDINGS_FILE, feedings)


if __name__ == "__main__":
    main()
