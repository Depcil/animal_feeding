"""Административная панель Django (admin_client – суперпользователь)."""
import pytest

from feedings.models import Feeding

pytestmark = pytest.mark.django_db


def test_admin_index_shows_russian_names(admin_client):
    text = admin_client.get("/admin/").content.decode()
    assert "PetFeed – администрирование" in text
    for name in ("Животные", "Сотрудники", "Журнал кормлений", "Кормления"):
        assert name in text


def test_admin_requires_login(client):
    response = client.get("/admin/feedings/feeding/")
    assert response.status_code == 302
    assert "/admin/login/" in response["Location"]


@pytest.mark.parametrize(
    "url",
    [
        "/admin/animals/animal/",
        "/admin/employees/employee/",
        "/admin/feedings/feeding/",
        "/admin/animals/animal/1/change/",
        "/admin/employees/employee/1/change/",
        "/admin/feedings/feeding/1/change/",
    ],
)
def test_admin_pages_open(admin_client, url):
    assert admin_client.get(url).status_code == 200


def test_admin_search_and_filter(admin_client):
    found = admin_client.get("/admin/animals/animal/", {"q": "Рекс"})
    assert found.context["cl"].result_count == 1
    cancelled = admin_client.get(
        "/admin/feedings/feeding/", {"is_cancelled__exact": "1"}
    )
    assert cancelled.context["cl"].result_count == 2


def test_animal_page_shows_related_feedings(admin_client):
    text = admin_client.get("/admin/animals/animal/2/change/").content.decode()
    assert "каша с мясом" in text


def test_cancel_action(admin_client):
    admin_client.post(
        "/admin/feedings/feeding/",
        {"action": "mark_cancelled", "_selected_action": ["1", "2"]},
    )
    cancelled = Feeding.objects.filter(pk__in=[1, 2], is_cancelled=True)
    assert cancelled.count() == 2
