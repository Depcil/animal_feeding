from django.shortcuts import render

from animals.models import Animal
from feedings.models import Feeding


def index(request):
    counts = {
        "animals_count": Animal.objects.count(),
        "active_feedings": Feeding.objects.active().count(),
    }
    # Пять последних активных кормлений для блока на главной странице.
    latest = (
        Feeding.objects
        .active()
        .select_related("animal")[:5]
    )

    return render(
        request,
        "homepage/index.html",
        {"counts": counts, "latest": latest},
    )


def page_not_found(request, exception):
    return render(
        request,
        "404.html",
        status=404,
    )
