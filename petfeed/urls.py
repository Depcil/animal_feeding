from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("homepage.urls")),
    path("animals/", include("animals.urls")),
    path("feedings/", include("feedings.urls")),
]

handler404 = "homepage.views.page_not_found"
