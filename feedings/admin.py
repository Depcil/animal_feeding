from django.contrib import admin

from .models import Feeding


@admin.register(Feeding)
class FeedingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "feeding_date",
        "animal",
        "employee",
        "food",
        "amount",
        "is_cancelled",
    )
    list_display_links = ("id", "feeding_date")
    # Животное и сотрудник загружаются вместе со списком (JOIN),
    # а не отдельным запросом на каждую строку.
    list_select_related = ("animal", "employee")
    list_filter = (
        "is_cancelled",
        "feeding_date",
        "animal__species",
        "employee",
    )
    search_fields = ("animal__name", "employee__name", "food", "comment")
    date_hierarchy = "feeding_date"
    autocomplete_fields = ("animal", "employee")
    ordering = ("-feeding_date", "-id")
    list_per_page = 20
    actions = ("mark_cancelled",)

    @admin.action(description="Отменить выбранные кормления")
    def mark_cancelled(self, request, queryset):
        updated = queryset.update(is_cancelled=True)
        self.message_user(request, f"Отменено кормлений: {updated}")
