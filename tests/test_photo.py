from io import BytesIO

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

from animals.models import Animal

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def media_root(settings, tmp_path):
    # Загруженные в тестах файлы не должны попадать в папку media проекта.
    settings.MEDIA_ROOT = tmp_path


def png_file(name="cat.png", size=(20, 20)):
    buffer = BytesIO()
    Image.new("RGB", size, "orange").save(buffer, format="PNG")
    return SimpleUploadedFile(name, buffer.getvalue(), "image/png")


def test_photo_page_has_multipart_form(client):
    text = client.get("/animals/barsik-1/photo/").content.decode()
    assert 'enctype="multipart/form-data"' in text
    assert "csrfmiddlewaretoken" in text


def test_upload_photo(client):
    response = client.post(
        "/animals/barsik-1/photo/", {"photo": png_file()},
    )
    assert response.status_code == 302
    assert response.url == "/animals/barsik-1/"
    animal = Animal.objects.get(slug="barsik-1")
    assert animal.photo.name.startswith("animals/cat")
    detail = client.get("/animals/barsik-1/").content.decode()
    assert animal.photo.url in detail
    assert "Фото сохранено." in detail


def test_not_an_image_rejected(client):
    fake = SimpleUploadedFile("cat.png", b"not an image", "image/png")
    response = client.post("/animals/barsik-1/photo/", {"photo": fake})
    assert response.status_code == 200
    assert "Загрузите правильное изображение" in response.content.decode()
    assert not Animal.objects.get(slug="barsik-1").photo


def test_too_big_photo_rejected(client, monkeypatch):
    monkeypatch.setattr("animals.forms.MAX_PHOTO_SIZE", 10)
    response = client.post(
        "/animals/barsik-1/photo/", {"photo": png_file()},
    )
    assert response.status_code == 200
    assert "Файл слишком большой" in response.content.decode()
