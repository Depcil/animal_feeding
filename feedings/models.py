from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Sum
from django.db.models.functions import Coalesce

from animals.models import Animal
from employees.models import Employee


class FeedingQuerySet(models.QuerySet):
    """Часто используемые выборки кормлений."""

    def active(self):
        """Кормления, которые занимают суточную норму (кроме отмененных)."""
        return self.exclude(status=self.model.Status.CANCELLED)

    def planned(self):
        return self.filter(status=self.model.Status.PLANNED)

    def done(self):
        return self.filter(status=self.model.Status.DONE)

    def cancelled(self):
        return self.filter(status=self.model.Status.CANCELLED)

    def for_date(self, feeding_date):
        return self.filter(feeding_date=feeding_date)

    def fed_amount(self):
        """Сумма порций активных кормлений выборки, г."""
        return self.active().aggregate(
            total=Coalesce(Sum("amount"), 0),
        )["total"]


class FeedingManager(models.Manager.from_queryset(FeedingQuerySet)):
    pass


class Feeding(models.Model):
    class Status(models.TextChoices):
        PLANNED = "planned", "Запланировано"
        DONE = "done", "Выполнено"
        CANCELLED = "cancelled", "Отменено"

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
        help_text="Вместе с другими кормлениями за день не больше нормы.",
    )
    status = models.CharField(
        max_length=12,
        choices=Status.choices,
        default=Status.PLANNED,
        verbose_name="Статус",
    )
    comment = models.TextField(
        blank=True,
        verbose_name="Комментарий",
    )

    objects = FeedingManager()

    class Meta:
        ordering = ["-feeding_date", "-pk"]
        verbose_name = "Кормление"
        verbose_name_plural = "Кормления"

    def __str__(self):
        return f"{self.animal.name} – {self.feeding_date}, {self.amount} г"

    @property
    def is_cancelled(self):
        return self.status == self.Status.CANCELLED

    def cancel(self):
        """Отменить кормление: запись остается, но норму не занимает."""
        self.status = self.Status.CANCELLED
        self.save(update_fields=["status"])

    def mark_done(self):
        self.status = self.Status.DONE
        self.save(update_fields=["status"])


# Статусы, при которых кормление занимает суточную норму.
ACTIVE_STATUSES = [Feeding.Status.PLANNED, Feeding.Status.DONE]
