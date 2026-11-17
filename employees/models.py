from django.db import models


class Employee(models.Model):
    """Сотрудник приюта, который кормит животных.

    Это сущность предметной области, а не учетная запись для входа
    в систему (для админки используется встроенный django.contrib.auth).
    """

    name = models.CharField(
        max_length=100,
        verbose_name="Имя",
    )
    email = models.EmailField(
        unique=True,
        verbose_name="Электронная почта",
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"

    def __str__(self):
        return self.name
