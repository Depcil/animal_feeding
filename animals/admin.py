from django.contrib import admin
from django.db.models import Count

from feedings.models import Feeding

from .models import Animal


class AnimalFeedingInline(admin.TabularInline):
    """Кормления животного на странице животного (только просмотр)."""

    model = Feeding
    fields = ("feeding_date", "food", "amount", "employee", "is_cancelled")
    readonly_fields = fields
    extra = 0
    can_delete = False
    show_change_link = True

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "species", "daily_norm", "feedings_count")
    list_display_links = ("name",)
    list_editable = ("daily_norm",)
    search_fields = ("name", "species")
    list_filter = ("species",)
    ordering = ("name",)
    list_per_page = 20
    inlines = [AnimalFeedingInline]

    def get_queryset(self, request):
        # Число кормлений считается одним запросом вместе со списком.
        return super().get_queryset(request).annotate(
            feedings_total=Count("feedings"),
        )

    @admin.display(description="Кормлений", ordering="feedings_total")
    def feedings_count(self, obj):
        return obj.feedings_total
