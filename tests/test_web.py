from django.template.loader import render_to_string
from django.test import Client, override_settings

client = Client()


def template_names(response):
    return [t.name for t in response.templates if t.name]


def test_homepage_uses_base_template():
    response = client.get("/")
    text = response.content.decode()
    assert response.status_code == 200
    assert "homepage/index.html" in template_names(response)
    assert "base.html" in template_names(response)
    assert "includes/navigation.html" in template_names(response)
    assert "<title>\n    Главная – PetFeed" in text.replace("\r", "")


def test_navigation_links_built_by_url_names():
    text = client.get("/").content.decode()
    assert 'href="/animals/"' in text
    assert 'href="/feedings/"' in text


def test_animals_list_filter_length_and_cards():
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
    from models import Animal
    text = render_to_string(
        "animals/includes/animal_card.html",
        {"animal": Animal(7, "", "кот", 100)},
    )
    assert "Без клички" in text


def test_animal_detail_and_404():
    ok = client.get("/animals/1/")
    assert ok.status_code == 200
    assert "Суточная норма" in ok.content.decode()
    missing = client.get("/animals/9999/")
    assert missing.status_code == 404
    assert "Животное не найдено" in missing.content.decode()


def test_feedings_list_status_include():
    response = client.get("/feedings/")
    text = response.content.decode()
    assert response.status_code == 200
    assert "feedings/includes/feeding_status.html" in template_names(response)
    assert "Активно" in text and "Отменено" in text


def test_feeding_detail_related_objects_and_404():
    ok = client.get("/feedings/1/")
    text = ok.content.decode()
    assert ok.status_code == 200
    assert "Барсик" in text and "Анна Смирнова" in text
    missing = client.get("/feedings/9999/")
    assert missing.status_code == 404
    assert "Кормление не найдено" in missing.content.decode()


def test_static_files_connected():
    text = client.get("/").content.decode()
    assert "/static/homepage/css/style.css" in text
    assert "/static/homepage/js/main.js" in text
    assert "/static/homepage/img/logo.png" in text


@override_settings(DEBUG=False, ALLOWED_HOSTS=["testserver"])
def test_custom_404_template():
    response = client.get("/nonexistent/")
    assert response.status_code == 404
    assert "404.html" in template_names(response)
