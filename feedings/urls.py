from django.urls import path

from . import views

urlpatterns = [
    path("", views.feedings, name="feedings"),
    path("<int:feeding_id>/", views.feeding_detail, name="feeding_detail"),
]
