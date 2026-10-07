from django.shortcuts import render

from models.feedings import find_feeding_by_id
from storage import load_animals, load_feedings, load_users


def _load_feedings():
    animals_list = load_animals("data/animals.json")
    users_list = load_users("data/users.json")
    return load_feedings(
        "data/feedings.json",
        animals_list,
        users_list,
    )


def feedings(request):
    context = {
        "feedings": _load_feedings(),
    }

    return render(
        request,
        "feedings/feeding_list.html",
        context,
    )


def feeding_detail(request, feeding_id):
    feeding = find_feeding_by_id(_load_feedings(), feeding_id)

    context = {
        "feeding": feeding,
    }

    return render(
        request,
        "feedings/feeding_detail.html",
        context,
        status=404 if feeding is None else 200,
    )
