from datetime import date

from django.shortcuts import render

from models.animals import find_animal_by_id
from models.feedings import get_fed_amount, get_remaining_norm
from storage import load_animals, load_feedings, load_users


def animals(request):
    animals_list = load_animals("data/animals.json")

    context = {
        "animals": animals_list,
    }

    return render(
        request,
        "animals/animal_list.html",
        context,
    )


def animal_detail(request, animal_id):
    animals_list = load_animals("data/animals.json")
    animal = find_animal_by_id(animals_list, animal_id)

    context = {
        "animal": animal,
    }

    if animal is not None:
        users_list = load_users("data/users.json")
        feedings_list = load_feedings(
            "data/feedings.json",
            animals_list,
            users_list,
        )
        today = date.today().isoformat()
        context["fed"] = get_fed_amount(feedings_list, animal, today)
        context["remaining"] = get_remaining_norm(
            feedings_list,
            animal,
            today,
        )

    return render(
        request,
        "animals/animal_detail.html",
        context,
        status=404 if animal is None else 200,
    )
