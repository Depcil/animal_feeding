from django import forms

from animals.models import Animal
from employees.models import Employee


class FeedingFilterForm(forms.Form):
    """Фильтр журнала кормлений. Значения приходят GET-параметрами."""

    STATUS_CHOICES = [
        ("all", "Все"),
        ("active", "Активные"),
        ("planned", "Запланированные"),
        ("done", "Выполненные"),
        ("cancelled", "Отмененные"),
    ]
    SORT_CHOICES = [
        ("date", "по дате"),
        ("animal", "по животному"),
        ("employee", "по сотруднику"),
        ("amount", "по порции"),
    ]

    date = forms.DateField(
        required=False,
        label="Дата",
        widget=forms.DateInput(
            attrs={"type": "date", "class": "form-control"},
            format="%Y-%m-%d",
        ),
    )
    animal = forms.ModelChoiceField(
        queryset=Animal.objects.order_by("name"),
        required=False,
        empty_label="Все",
        label="Животное",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    employee = forms.ModelChoiceField(
        queryset=Employee.objects.order_by("name"),
        required=False,
        empty_label="Все",
        label="Сотрудник",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        label="Статус",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    sort = forms.ChoiceField(
        choices=SORT_CHOICES,
        required=False,
        label="Сортировка",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
