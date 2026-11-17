"""Модели Django, перенос данных из базы ПР7 и страницы на ORM."""
import json
from datetime import date

import pytest
from django.db.models import ProtectedError

from animals.models import Animal
from db.database import BASE_DIR
from employees.models import Employee
from feedings.models import Feeding

pytestmark = pytest.mark.django_db


def json_count(name):
    with open(BASE_DIR / "data" / name, encoding="utf-8") as file:
        return len(json.load(file))


def test_transfer_keeps_counts_and_links():
    assert Animal.objects.count() == json_count("animals.json")
    assert Employee.objects.count() == json_count("users.json")
    assert Feeding.objects.count() == json_count("feedings.json")
    feeding = Feeding.objects.select_related("animal", "employee").get(pk=3)
    assert feeding.animal.name == "Мурка"
    assert feeding.employee.name == "Анна Смирнова"
    assert feeding.feeding_date == date(2026, 10, 6)
    assert feeding.status == Feeding.Status.CANCELLED
    # Неотмененные кормления ПР7 переносятся как выполненные.
    assert Feeding.objects.get(pk=1).status == Feeding.Status.DONE


def test_reverse_relations():
    rex = Animal.objects.get(name="Рекс")
    assert rex.feedings.count() == 3
    anna = Employee.objects.get(email="anna@example.com")
    assert anna.feedings.active().count() == 3


def test_feeding_manager_methods():
    assert Feeding.objects.active().count() == 8
    assert Feeding.objects.done().count() == 8
    assert Feeding.objects.cancelled().count() == 2
    assert Feeding.objects.planned().count() == 0
    day = Feeding.objects.for_date(date(2026, 10, 7))
    assert day.count() == 4
    # Барсик 07.10: 120 г + 80 г, отмененных в этот день нет.
    assert day.filter(animal_id=1).fed_amount() == 200
    # 08.10 у Барсика только отмененное кормление – в норму не входит.
    barsik_08 = Feeding.objects.for_date(date(2026, 10, 8)).filter(animal_id=1)
    assert barsik_08.count() == 1 and barsik_08.fed_amount() == 0


def test_cancel_method_and_protect():
    feeding = Feeding.objects.get(pk=1)
    feeding.cancel()
    feeding.refresh_from_db()
    assert feeding.is_cancelled
    with pytest.raises(ProtectedError):
        Animal.objects.get(pk=1).delete()


def test_animals_search_norm_and_sort(client):
    found = client.get("/animals/", {"q": "соб"}).content.decode()
    assert "Всего животных: 1" in found and "Рекс" in found
    by_norm = client.get("/animals/", {"min_norm": "200"}).content.decode()
    assert "Всего животных: 2" in by_norm
    response = client.get("/animals/", {"sort": "norm"})
    names = [animal.name for animal in response.context["animals"]]
    assert names == ["Рекс", "Барсик", "Мурка", "Кеша"]
    # Неизвестное значение sort не попадает в order_by().
    assert client.get("/animals/", {"sort": "id; DROP"}).status_code == 200


def test_search_has_no_sql_injection(client):
    text = client.get("/animals/", {"q": "' OR 1=1 --"}).content.decode()
    assert "Животные не найдены." in text


def test_available_animals_by_date(client):
    empty = client.get("/animals/available/").content.decode()
    assert "Дата: " not in empty
    response = client.get("/animals/available/", {"date": "2026-10-07"})
    remaining = {a.name: a.remaining for a in response.context["animals"]}
    # Барсик уже получил 200 г из 200 г, остальные еще нет.
    assert remaining == {"Кеша": 40, "Мурка": 120, "Рекс": 300}
    bad = client.get("/animals/available/", {"date": "abc"}).content.decode()
    assert "Дата указана неверно" in bad


def test_animal_detail_by_date(client):
    text = client.get("/animals/1/", {"date": "2026-10-07"}).content.decode()
    assert "получил:</strong> 200 г" in text
    assert "норма выполнена" in text


def test_feedings_filters(client):
    def total(**params):
        return client.get("/feedings/", params).context["total"]

    assert total(status="active") == 8
    assert total(status="cancelled") == 2
    assert total(status="done") == 8
    assert total(status="planned") == 0
    assert total(animal="2") == 3
    assert total(employee="1") == 5
    assert total(date="2026-10-08") == 5
    assert total(animal="2", date="2026-10-08") == 2
    bad = client.get("/feedings/", {"date": "08.10.2026"})
    assert bad.status_code == 200 and bad.context["error"]


def test_feedings_sort_and_pagination(client):
    first = client.get("/feedings/", {"sort": "amount"}).context["feedings"][0]
    assert first.amount == 300
    page2 = client.get("/feedings/", {"page": "2"}).content.decode()
    assert "Страница 2 из 2" in page2

    def page_number(page):
        response = client.get("/feedings/", {"page": page})
        return response.context["page_obj"].number

    assert page_number("abc") == 1
    assert page_number("99") == 2
    # Параметры фильтра и сортировки сохраняются в ссылках пагинации.
    text = client.get(
        "/feedings/", {"status": "active", "sort": "amount"}
    ).content.decode()
    assert "?status=active&amp;sort=amount&amp;page=2" in text


def test_statistics_page(client):
    response = client.get("/feedings/statistics/")
    summary = response.context["summary"]
    assert summary == {
        "total_count": 10,
        "planned_count": 0,
        "done_count": 8,
        "cancelled_count": 2,
        "total_amount": 1235,
    }
    text = response.content.decode()
    assert "Рекс" in text and "850" in text
    strict = client.get(
        "/feedings/statistics/", {"min_count": "3"}
    ).content.decode()
    assert "Рекс – 3" in strict and "Барсик – 2" not in strict
