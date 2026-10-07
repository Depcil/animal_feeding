"""PR1: проверка возможности кормления животного."""
from datetime import date

animal_name = "Барсик"
species = "кот"
daily_norm = 200
fed_today = int("120")
portion = int("100")
feeding_date = date(2026, 10, 7)


def calc_remaining_norm(daily_norm, fed_today):
    """Вернуть остаток суточной нормы в граммах."""
    remaining = daily_norm - fed_today
    if remaining < 0:
        return 0
    return remaining


def is_portion_allowed(daily_norm, fed_today, portion):
    """Проверить, что порция не превысит суточную норму."""
    return fed_today + portion <= daily_norm


def get_feeding_status(is_allowed):
    """Вернуть текстовый статус кормления."""
    if is_allowed:
        return "Кормление разрешено"
    return "Суточная норма будет превышена"


def format_animal_card(animal_name, species, daily_norm):
    """Сформировать строку с карточкой животного."""
    return f"{animal_name} ({species}), норма {daily_norm} г/сутки"


print(format_animal_card(animal_name, species, daily_norm))
print(f"Дата: {feeding_date}")
print(f"Уже получено: {fed_today} г, порция: {portion} г")
print(f"Остаток нормы: {calc_remaining_norm(daily_norm, fed_today)} г")
print(get_feeding_status(is_portion_allowed(daily_norm, fed_today, portion)))
