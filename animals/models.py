from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Case, Value, When
from django.urls import reverse
from django.utils.text import slugify
from unidecode import unidecode

# Норма, начиная с которой у животного «большая норма», г.
LARGE_NORM = 500


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
    # Значение считает сама база данных при каждом изменении нормы.
    is_large_norm = models.GeneratedField(
        expression=Case(
            When(daily_norm__gte=LARGE_NORM, then=Value(True)),
            default=Value(False),
            output_field=models.BooleanField(),
        ),
        output_field=models.BooleanField(),
        db_persist=True,
        verbose_name="Большая норма",
    )
    photo = models.ImageField(
        upload_to="animals/",
        blank=True,
        verbose_name="Фото",
    )
    slug = models.SlugField(
        max_length=120,
        unique=True,
        editable=False,
        verbose_name="URL-идентификатор",
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Животное"
        verbose_name_plural = "Животные"

    def __str__(self):
        return f"{self.name} ({self.species})"

    def make_slug(self):
        """«Барсик» с id 1 -> barsik-1 (id делает адрес уникальным)."""
        return f"{slugify(unidecode(self.name)) or 'animal'}-{self.pk}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # id известен только после первого сохранения, поэтому slug
        # новой записи дописывается отдельным запросом. У существующих
        # животных slug не меняется, чтобы не ломать старые ссылки.
        if not self.slug:
            self.slug = self.make_slug()
            super().save(update_fields=["slug"])

    def get_absolute_url(self):
        return reverse("animals:detail", kwargs={"slug": self.slug})
