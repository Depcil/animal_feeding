from django.urls import path

from . import views

app_name = "animals"

urlpatterns = [
    path("", views.animals, name="list"),
    path("available/", views.available_animals, name="available"),
    path("<int:animal_id>/", views.animal_detail, name="detail"),
]
