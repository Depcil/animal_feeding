from django.urls import path

from . import views

urlpatterns = [
    path("", views.animals, name="animals"),
    path("<int:animal_id>/", views.animal_detail, name="animal_detail"),
]
