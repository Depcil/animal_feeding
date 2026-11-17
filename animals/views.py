from datetime import date

from django.db.models import F, Q, Sum
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404, render

from feedings.models import ACTIVE_STATUSES

from .models import Animal

# Допустимые значения параметра sort -> поля сортировки.
# В order_by() попадают только эти поля, а не строка из запроса.
SORT_FIELDS = {
    "name": ["name"],
    "norm": ["-daily_norm", "name"],
    "species": ["species", "name"],
}


def _parse_date(value):
    """Строка YYYY-MM-DD -> date или None, если формат неверный."""
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        return None


def animals(request):
    query = request.GET.get("q", "").strip()
    min_norm_raw = request.GET.get("min_norm", "").strip()
    sort = request.GET.get("sort", "name")
    if sort not in SORT_FIELDS:
        sort = "name"

    animals_list = Animal.objects.all()
    if query:
        # Поиск по двум полям сразу: кличка или вид.
        animals_list = animals_list.filter(
            Q(name__icontains=query) | Q(species__icontains=query)
        )
    if min_norm_raw.isdigit():
        animals_list = animals_list.filter(daily_norm__gte=int(min_norm_raw))
    animals_list = animals_list.order_by(*SORT_FIELDS[sort])

    context = {
        "animals": animals_list,
        "query": query,
        "min_norm": min_norm_raw,
        "sort": sort,
    }

    return render(
        request,
        "animals/animal_list.html",
        context,
    )


def animal_detail(request, animal_id):
    animal = get_object_or_404(Animal, pk=animal_id)
    feeding_date = _parse_date(request.GET.get("date")) or date.today()

    day_feedings = (
        animal.feedings
        .for_date(feeding_date)
        .select_related("employee")
        .order_by("pk")
    )
    fed = day_feedings.fed_amount()

    context = {
        "animal": animal,
        "feeding_date": feeding_date,
        "fed": fed,
        "remaining": max(animal.daily_norm - fed, 0),
        "day_feedings": day_feedings,
    }

    return render(
        request,
        "animals/animal_detail.html",
        context,
    )


def available_animals(request):
    raw_date = request.GET.get("date", "")
    feeding_date = _parse_date(raw_date)
    animals_list = []
    if feeding_date:
        # LEFT JOIN с условием: животные без кормлений за дату тоже
        # попадают в выборку, у них fed = 0. Отмененные не считаются.
        animals_list = (
            Animal.objects
            .annotate(
                fed=Coalesce(
                    Sum(
                        "feedings__amount",
                        filter=Q(
                            feedings__feeding_date=feeding_date,
                            feedings__status__in=ACTIVE_STATUSES,
                        ),
                    ),
                    0,
                ),
            )
            .annotate(remaining=F("daily_norm") - F("fed"))
            .filter(remaining__gt=0)
            .order_by("name")
        )

    context = {
        "animals": animals_list,
        "feeding_date": feeding_date,
        "date_error": bool(raw_date) and feeding_date is None,
        "today": date.today(),
    }

    return render(
        request,
        "animals/available.html",
        context,
    )
