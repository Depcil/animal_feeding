from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "PetFeed – администрирование"
admin.site.site_title = "PetFeed"
admin.site.index_title = "Учет кормления животных"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("homepage.urls")),
    path("animals/", include("animals.urls")),
    path("feedings/", include("feedings.urls")),
]

handler404 = "homepage.views.page_not_found"
