from datetime import date

from django import forms
from django.core.exceptions import ValidationError

from animals.models import Animal
from employees.models import Employee

from .models import Feeding


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


# Больше этого за одно кормление не дают ни одному животному приюта.
MAX_PORTION = 2000


def validate_portion(value):
    """Пользовательский валидатор: порция не больше MAX_PORTION граммов."""
    if value > MAX_PORTION:
        raise ValidationError(
            f"Слишком большая порция: не больше {MAX_PORTION} г "
            f"за одно кормление."
        )


class FeedingForm(forms.ModelForm):
    """Создание и редактирование запланированного кормления.

    Статус в форму не входит: новое кормление всегда «Запланировано»,
    а выполнение и отмена делаются отдельными кнопками.
    """

    class Meta:
        model = Feeding
        fields = ("animal", "employee", "feeding_date", "food", "amount",
                  "comment")
        widgets = {
            "animal": forms.Select(attrs={"class": "form-select"}),
            "employee": forms.Select(attrs={"class": "form-select"}),
            "feeding_date": forms.DateInput(
                attrs={"type": "date", "class": "form-control"},
                format="%Y-%m-%d",
            ),
            "food": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "например, сухой корм",
            }),
            "amount": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 1,
            }),
            "comment": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
            }),
        }
        help_texts = {
            "feeding_date": "Кормление можно запланировать на сегодня "
                            "или на будущие дни.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["amount"].validators.append(validate_portion)

    def clean_feeding_date(self):
        feeding_date = self.cleaned_data["feeding_date"]
        if feeding_date < date.today():
            raise ValidationError(
                "Нельзя запланировать кормление на прошедшую дату."
            )
        return feeding_date

    def clean_food(self):
        food = self.cleaned_data["food"]
        if not any(char.isalpha() for char in food):
            raise ValidationError("Название корма должно содержать буквы.")
        return food

    def clean(self):
        cleaned_data = super().clean()
        animal = cleaned_data.get("animal")
        feeding_date = cleaned_data.get("feeding_date")
        amount = cleaned_data.get("amount")
        # Если одно из полей не прошло проверку, правило нормы не проверяем:
        # ошибка уже показана у самого поля.
        if not (animal and feeding_date and amount):
            return cleaned_data

        # При редактировании само кормление из суммы исключается,
        # иначе его порция была бы посчитана дважды.
        fed = (
            Feeding.objects
            .filter(animal=animal)
            .for_date(feeding_date)
            .exclude(pk=self.instance.pk)
            .fed_amount()
        )
        remaining = animal.daily_norm - fed
        if amount > remaining:
            raise ValidationError(
                f"Превышена суточная норма: {animal.name} на "
                f"{feeding_date:%d.%m.%Y} уже получает {fed} г из "
                f"{animal.daily_norm} г, можно добавить не больше "
                f"{max(remaining, 0)} г."
            )
        return cleaned_data
