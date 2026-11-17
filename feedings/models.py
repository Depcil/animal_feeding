from django.core.validators import MinValueValidator
from django.db import models

from animals.models import Animal
from employees.models import Employee


class Feeding(models.Model):
    # PROTECT: нельзя удалить животное или сотрудника,
    # пока на них ссылаются записи журнала кормлений.
    animal = models.ForeignKey(
        Animal,
        on_delete=models.PROTECT,
        related_name="feedings",
        verbose_name="Животное",
    )
    employee = models.ForeignKey(
        Employee,
        on_delete=models.PROTECT,
        related_name="feedings",
        verbose_name="Сотрудник",
    )
    feeding_date = models.DateField(
        verbose_name="Дата кормления",
    )
    food = models.CharField(
        max_length=100,
        verbose_name="Корм",
    )
    amount = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Порция, г",
    )
    is_cancelled = models.BooleanField(
        default=False,
        verbose_name="Кормление отменено",
    )
    comment = models.TextField(
        blank=True,
        verbose_name="Комментарий",
    )

    class Meta:
        ordering = ["-feeding_date", "-pk"]
        verbose_name = "Кормление"
        verbose_name_plural = "Кормления"

    def __str__(self):
        return f"{self.animal.name} – {self.feeding_date}, {self.amount} г"

    def cancel(self):
        """Отменить кормление: запись остается, но норму не занимает."""
        self.is_cancelled = True
        self.save(update_fields=["is_cancelled"])
