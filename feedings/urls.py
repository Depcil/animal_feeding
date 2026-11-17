from django.urls import path

from . import views

app_name = "feedings"

urlpatterns = [
    path("", views.feedings, name="list"),
    path("new/", views.feeding_create, name="create"),
    path("statistics/", views.statistics, name="statistics"),
    path("<int:feeding_id>/", views.feeding_detail, name="detail"),
    path("<int:feeding_id>/edit/", views.feeding_update, name="update"),
    path("<int:feeding_id>/cancel/", views.feeding_cancel, name="cancel"),
    path("<int:feeding_id>/done/", views.feeding_done, name="done"),
]
