"""Формы ПР11: фильтр журнала, создание и редактирование кормлений."""
import pytest

from feedings.forms import FeedingFilterForm

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
