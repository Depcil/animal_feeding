from django.urls import path

from . import views

app_name = "animals"

urlpatterns = [
    path("", views.animals, name="list"),
    path("available/", views.available_animals, name="available"),
    # Старые адреса вида /animals/1/ перенаправляются на адрес со slug.
    path("<int:animal_id>/", views.animal_by_id, name="by_id"),
    path("<slug:slug>/", views.animal_detail, name="detail"),
    path("<slug:slug>/photo/", views.animal_photo, name="photo"),
]
