from django.core.validators import MinValueValidator
from django.db import models


class Animal(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name="Кличка",
    )
    species = models.CharField(
        max_length=50,
        verbose_name="Вид",
    )
    # Суточная норма корма в граммах, должна быть больше нуля.
    daily_norm = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Суточная норма, г",
        help_text="Сколько граммов корма животное может получить за сутки.",
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Животное"
        verbose_name_plural = "Животные"

    def __str__(self):
        return f"{self.name} ({self.species})"
