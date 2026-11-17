from datetime import date

from django.core.paginator import Paginator
from django.db.models import Avg, Count, Max, Min, Q, Sum
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404, render

from animals.models import Animal
from employees.models import Employee

from .models import Feeding

PAGE_SIZE = 5

SORT_FIELDS = {
    "date": ["-feeding_date", "-pk"],
    "animal": ["animal__name", "-feeding_date"],
    "employee": ["employee__name", "-feeding_date"],
    "amount": ["-amount", "-feeding_date"],
}

ACTIVE = Q(is_cancelled=False)


def _positive_int(value, default):
    return int(value) if value and value.isdigit() and int(value) > 0 \
        else default


def feedings(request):
    status = request.GET.get("status", "all")
    raw_date = request.GET.get("date", "")
    animal_id = request.GET.get("animal", "")
    employee_id = request.GET.get("employee", "")
    sort = request.GET.get("sort", "date")
    if sort not in SORT_FIELDS:
        sort = "date"
    error = None

    # select_related: животное и сотрудник приходят одним запросом с JOIN,
    # без отдельного обращения к базе для каждой строки списка.
    feedings_list = Feeding.objects.select_related("animal", "employee")

    if status == "active":
        feedings_list = feedings_list.exclude(is_cancelled=True)
    elif status == "cancelled":
        feedings_list = feedings_list.filter(is_cancelled=True)
    else:
        status = "all"

    if raw_date:
        try:
            feedings_list = feedings_list.filter(
                feeding_date=date.fromisoformat(raw_date),
            )
        except ValueError:
            error = "Дата указана неверно, используйте формат ГГГГ-ММ-ДД."
    if animal_id.isdigit():
        feedings_list = feedings_list.filter(animal_id=int(animal_id))
    if employee_id.isdigit():
        feedings_list = feedings_list.filter(employee_id=int(employee_id))

    feedings_list = feedings_list.order_by(*SORT_FIELDS[sort])

    # get_page() сам обрабатывает page=abc и номер больше последнего.
    page_obj = Paginator(feedings_list, PAGE_SIZE).get_page(
        request.GET.get("page"),
    )

    context = {
        "page_obj": page_obj,
        "feedings": page_obj.object_list,
        "total": page_obj.paginator.count,
        "status": status,
        "selected_date": raw_date,
        "selected_animal": animal_id,
        "selected_employee": employee_id,
        "sort": sort,
        "animals": Animal.objects.order_by("name"),
        "employees": Employee.objects.order_by("name"),
        "error": error,
    }

    return render(
        request,
        "feedings/feeding_list.html",
        context,
    )


def feeding_detail(request, feeding_id):
    feeding = get_object_or_404(
        Feeding.objects.select_related("animal", "employee"),
        pk=feeding_id,
    )

    return render(
        request,
        "feedings/feeding_detail.html",
        {"feeding": feeding},
    )


def statistics(request):
    min_count = _positive_int(request.GET.get("min_count"), 2)

    summary = Feeding.objects.aggregate(
        total_count=Count("id"),
        active_count=Count("id", filter=ACTIVE),
        cancelled_count=Count("id", filter=Q(is_cancelled=True)),
        total_amount=Coalesce(Sum("amount", filter=ACTIVE), 0),
    )
    norms = Animal.objects.aggregate(
        animals_count=Count("id"),
        min_norm=Min("daily_norm"),
        max_norm=Max("daily_norm"),
        avg_norm=Avg("daily_norm"),
    )

    # Условие в filter= внутри агрегата сохраняет в списке животных
    # и сотрудников без активных кормлений (у них 0).
    active_feedings = Q(feedings__is_cancelled=False)
    by_animal = Animal.objects.annotate(
        feedings_count=Count("feedings", filter=active_feedings),
        total_amount=Coalesce(
            Sum("feedings__amount", filter=active_feedings), 0,
        ),
    ).order_by("-feedings_count", "name")
    by_employee = Employee.objects.annotate(
        feedings_count=Count("feedings", filter=active_feedings),
        total_amount=Coalesce(
            Sum("feedings__amount", filter=active_feedings), 0,
        ),
    ).order_by("-feedings_count", "name")

    context = {
        "summary": summary,
        "norms": norms,
        "by_animal": by_animal,
        "by_employee": by_employee,
        "by_species": (
            Animal.objects
            .values("species")
            .annotate(animals_count=Count("id"))
            .order_by("-animals_count", "species")
        ),
        "by_date": (
            Feeding.objects
            .filter(ACTIVE)
            .values("feeding_date")
            .annotate(feedings_count=Count("id"), total_amount=Sum("amount"))
            .order_by("feeding_date")
        ),
        "frequent": by_animal.filter(feedings_count__gte=min_count),
        "min_count": min_count,
    }

    return render(
        request,
        "feedings/statistics.html",
        context,
    )
