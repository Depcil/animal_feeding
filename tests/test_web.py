from django.test import Client, override_settings

client = Client()


def test_homepage():
    response = client.get("/")
    assert response.status_code == 200
    assert "PetFeed" in response.content.decode()


def test_animals_list_from_json():
    response = client.get("/animals/")
    text = response.content.decode()
    assert response.status_code == 200
    assert "Барсик" in text and "Рекс" in text


def test_animal_detail():
    response = client.get("/animals/1/")
    text = response.content.decode()
    assert response.status_code == 200
    assert "Суточная норма" in text


def test_animal_not_found_returns_404():
    response = client.get("/animals/999/")
    assert response.status_code == 404
    assert "Животное не найдено" in response.content.decode()


def test_feedings_pages():
    assert client.get("/feedings/").status_code == 200
    detail = client.get("/feedings/1/")
    assert detail.status_code == 200
    assert "Анна Смирнова" in detail.content.decode()
    assert client.get("/feedings/999/").status_code == 404


@override_settings(DEBUG=False, ALLOWED_HOSTS=["testserver"])
def test_custom_404_page():
    response = client.get("/nonexistent/")
    assert response.status_code == 404
    assert "страница не найдена" in response.content.decode()
