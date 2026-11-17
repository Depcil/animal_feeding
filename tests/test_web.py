import pytest
from django.template.loader import render_to_string
from django.test import override_settings

pytestmark = pytest.mark.django_db


def template_names(response):
    return [t.name for t in response.templates if t.name]


def test_homepage_uses_base_template(client):
    response = client.get("/")
    text = response.content.decode()
    assert response.status_code == 200
    assert "homepage/index.html" in template_names(response)
    assert "base.html" in template_names(response)
    assert "includes/navigation.html" in template_names(response)
    assert "<title>\n    Главная – PetFeed" in text.replace("\r", "")


def test_navigation_links_built_by_url_names(client):
    text = client.get("/").content.decode()
    assert 'href="/animals/"' in text
    assert 'href="/feedings/"' in text
    assert 'href="/feedings/statistics/"' in text


def test_animals_list_filter_length_and_cards(client):
    response = client.get("/animals/")
    text = response.content.decode()
    assert response.status_code == 200
    assert "animals/includes/animal_card.html" in template_names(response)
    assert "Всего животных: 4" in text
    assert 'href="/animals/1/"' in text


def test_empty_animals_list():
    text = render_to_string("animals/animal_list.html", {"animals": []})
    assert "Животные не найдены." in text
    assert "Всего животных: 0" in text


def test_default_filter_for_empty_name():
    from animals.models import Animal
    text = render_to_string(
        "animals/includes/animal_card.html",
        {"animal": Animal(pk=7, name="", species="кот", daily_norm=100)},
    )
    assert "Без клички" in text


def test_animal_detail_and_404(client):
    ok = client.get("/animals/1/")
    assert ok.status_code == 200
    assert "Суточная норма" in ok.content.decode()
    missing = client.get("/animals/9999/")
    assert missing.status_code == 404
    assert "404.html" in template_names(missing)


def test_feedings_list_status_include(client):
    response = client.get("/feedings/")
    text = response.content.decode()
    assert response.status_code == 200
    assert "feedings/includes/feeding_status.html" in template_names(response)
    assert "Выполнено" in text and "Отменено" in text


def test_feeding_detail_related_objects_and_404(client):
    ok = client.get("/feedings/1/")
    text = ok.content.decode()
    assert ok.status_code == 200
    assert "Барсик" in text and "Анна Смирнова" in text
    missing = client.get("/feedings/9999/")
    assert missing.status_code == 404


def test_static_files_connected(client):
    text = client.get("/").content.decode()
    assert "/static/homepage/css/style.css" in text
    assert "/static/homepage/js/main.js" in text
    assert "/static/homepage/img/logo.png" in text


@override_settings(DEBUG=False, ALLOWED_HOSTS=["testserver"])
def test_custom_404_template(client):
    response = client.get("/nonexistent/")
    assert response.status_code == 404
    assert "404.html" in template_names(response)
