"""Формы ПР11: фильтр журнала, создание и редактирование кормлений."""
from datetime import date

import pytest
from django.test import Client

from feedings.forms import FeedingFilterForm
from feedings.models import Feeding

pytestmark = pytest.mark.django_db


def test_filter_form_cleans_values():
    form = FeedingFilterForm({
        "date": "2026-10-08",
        "animal": "2",
        "status": "done",
        "sort": "amount",
    })
    assert form.is_valid()
    assert form.cleaned_data["animal"].name == "Рекс"
    assert str(form.cleaned_data["date"]) == "2026-10-08"
    # Дату можно ввести и в русском формате.
    assert FeedingFilterForm({"date": "08.10.2026"}).is_valid()


def test_filter_form_invalid_values_do_not_break_page(client):
    response = client.get(
        "/feedings/",
        {"date": "2026-13-45", "animal": "999", "status": "done"},
    )
    form = response.context["form"]
    assert response.status_code == 200
    assert set(form.errors) == {"date", "animal"}
    # Верное условие (status=done) все равно применено.
    assert response.context["total"] == 8
    assert "Остальные условия применены" in response.content.decode()


def test_filter_form_keeps_selected_values(client):
    text = client.get(
        "/feedings/", {"animal": "2", "sort": "amount"}
    ).content.decode()
    assert '<option value="2" selected>' in text
    assert '<option value="amount" selected>' in text


def feeding_data(**changes):
    data = {
        "animal": "4",
        "employee": "1",
        "feeding_date": date.today().isoformat(),
        "food": "зерновая смесь",
        "amount": "30",
        "comment": "",
    }
    data.update(changes)
    return data


def test_create_form_page(client):
    response = client.get("/feedings/new/", {"animal": "4"})
    text = response.content.decode()
    assert response.status_code == 200
    assert "csrfmiddlewaretoken" in text
    assert response.context["form"].initial["animal"] == "4"


def test_create_feeding(client):
    response = client.post("/feedings/new/", feeding_data(), follow=True)
    feeding = Feeding.objects.latest("pk")
    assert response.redirect_chain[-1][0] == f"/feedings/{feeding.pk}/"
    assert feeding.status == Feeding.Status.PLANNED
    assert feeding.amount == 30
    assert "запланировано" in response.content.decode()


@pytest.mark.parametrize(
    "changes, field",
    [
        ({"feeding_date": "2020-01-01"}, "feeding_date"),
        ({"amount": "0"}, "amount"),
        ({"amount": "2500"}, "amount"),
        ({"food": "123"}, "food"),
        ({"animal": ""}, "animal"),
    ],
)
def test_create_feeding_field_errors(client, changes, field):
    count = Feeding.objects.count()
    response = client.post("/feedings/new/", feeding_data(**changes))
    assert response.status_code == 200
    assert field in response.context["form"].errors
    assert Feeding.objects.count() == count


def test_daily_norm_is_checked(client):
    # У Кеши норма 40 г: после 30 г можно добавить только 10 г.
    client.post("/feedings/new/", feeding_data(amount="30"))
    response = client.post("/feedings/new/", feeding_data(amount="20"))
    errors = response.context["form"].non_field_errors()
    assert "можно добавить не больше 10 г" in errors[0]
    # Отмененное кормление норму не занимает.
    Feeding.objects.latest("pk").cancel()
    response = client.post("/feedings/new/", feeding_data(amount="40"))
    assert response.status_code == 302


def test_edit_excludes_itself_from_norm(client):
    client.post("/feedings/new/", feeding_data(amount="40"))
    feeding = Feeding.objects.latest("pk")
    response = client.get(f"/feedings/{feeding.pk}/edit/")
    assert response.context["form"].instance == feeding
    # Норма уже заполнена этим же кормлением, но при правке оно
    # не считается повторно.
    response = client.post(
        f"/feedings/{feeding.pk}/edit/",
        feeding_data(amount="35", food="просо"),
    )
    assert response.status_code == 302
    feeding.refresh_from_db()
    assert (feeding.amount, feeding.food) == (35, "просо")


def test_only_planned_feeding_can_be_edited(client):
    response = client.get("/feedings/1/edit/", follow=True)
    assert response.redirect_chain[-1][0] == "/feedings/1/"
    assert "только запланированное" in response.content.decode()
    assert client.get("/feedings/9999/edit/").status_code == 404


def test_cancel_and_done_require_post(client):
    assert client.get("/feedings/1/cancel/").status_code == 405
    client.post("/feedings/new/", feeding_data())
    feeding = Feeding.objects.latest("pk")
    client.post(f"/feedings/{feeding.pk}/done/")
    feeding.refresh_from_db()
    assert feeding.status == Feeding.Status.DONE
    client.post(f"/feedings/{feeding.pk}/cancel/")
    feeding.refresh_from_db()
    assert feeding.status == Feeding.Status.CANCELLED
    assert client.post("/feedings/9999/cancel/").status_code == 404


def test_post_without_csrf_token_is_rejected():
    csrf_client = Client(enforce_csrf_checks=True)
    response = csrf_client.post("/feedings/new/", feeding_data())
    assert response.status_code == 403
