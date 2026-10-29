from django.urls import path

from . import views

app_name = "feedings"

urlpatterns = [
    path("", views.feedings, name="list"),
    path("statistics/", views.statistics, name="statistics"),
    path("<int:feeding_id>/", views.feeding_detail, name="detail"),
]
