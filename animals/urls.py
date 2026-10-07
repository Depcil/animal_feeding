from django.urls import path

from . import views

app_name = "animals"

urlpatterns = [
    path("", views.animals, name="list"),
    path("<int:animal_id>/", views.animal_detail, name="detail"),
]
