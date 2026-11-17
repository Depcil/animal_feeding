from django.core.paginator import Paginator
from django.db.models import Avg, Count, Max, Min, Q, Sum
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404, render

from animals.models import Animal
from employees.models import Employee

from .forms import FeedingFilterForm
from .models import ACTIVE_STATUSES, Feeding

PAGE_SIZE = 5

SORT_FIELDS = {
    "date": ["-feeding_date", "-pk"],
    "animal": ["animal__name", "-feeding_date"],
    "employee": ["employee__name", "-feeding_date"],
    "amount": ["-amount", "-feeding_date"],
}

# Фильтр журнала по статусу -> метод FeedingQuerySet.
STATUS_FILTERS = {
    "active": "active",
    "planned": "planned",
    "done": "done",
    "cancelled": "cancelled",
}


def _positive_int(value, default):
    return int(value) if value and value.isdigit() and int(value) > 0 \
        else default


def feedings(request):
    form = FeedingFilterForm(request.GET or None)
    # Если часть полей заполнена неверно, is_valid() вернет False,
    # но cleaned_data все равно содержит поля, прошедшие проверку:
    # по ним список фильтруется, а ошибки показываются над списком.
    if form.is_bound:
        form.is_valid()
    filters = getattr(form, "cleaned_data", {})
    status = filters.get("status") or "all"
    sort = filters.get("sort") or "date"

    # select_related: животное и сотрудник приходят одним запросом с JOIN,
    # без отдельного обращения к базе для каждой строки списка.
    feedings_list = Feeding.objects.select_related("animal", "employee")

    if status in STATUS_FILTERS:
        feedings_list = getattr(feedings_list, STATUS_FILTERS[status])()
    if filters.get("date"):
        feedings_list = feedings_list.for_date(filters["date"])
    if filters.get("animal"):
        feedings_list = feedings_list.filter(animal=filters["animal"])
    if filters.get("employee"):
        feedings_list = feedings_list.filter(employee=filters["employee"])

    feedings_list = feedings_list.order_by(*SORT_FIELDS[sort])

    # get_page() сам обрабатывает page=abc и номер больше последнего.
    page_obj = Paginator(feedings_list, PAGE_SIZE).get_page(
        request.GET.get("page"),
    )

    context = {
        "form": form,
        "page_obj": page_obj,
        "feedings": page_obj.object_list,
        "total": page_obj.paginator.count,
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

    status = Feeding.Status
    summary = Feeding.objects.aggregate(
        total_count=Count("id"),
        planned_count=Count("id", filter=Q(status=status.PLANNED)),
        done_count=Count("id", filter=Q(status=status.DONE)),
        cancelled_count=Count("id", filter=Q(status=status.CANCELLED)),
        total_amount=Coalesce(
            Sum("amount", filter=Q(status__in=ACTIVE_STATUSES)), 0,
        ),
    )
    norms = Animal.objects.aggregate(
        animals_count=Count("id"),
        min_norm=Min("daily_norm"),
        max_norm=Max("daily_norm"),
        avg_norm=Avg("daily_norm"),
    )

    # Условие в filter= внутри агрегата сохраняет в списке животных
    # и сотрудников без активных кормлений (у них 0).
    active_feedings = Q(feedings__status__in=ACTIVE_STATUSES)
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
            .active()
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
