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
        "status",
    )
    list_display_links = ("id", "feeding_date")
    # Животное и сотрудник загружаются вместе со списком (JOIN),
    # а не отдельным запросом на каждую строку.
    list_select_related = ("animal", "employee")
    list_filter = (
        "status",
        "feeding_date",
        "animal__species",
        "employee",
    )
    search_fields = ("animal__name", "employee__name", "food", "comment")
    date_hierarchy = "feeding_date"
    autocomplete_fields = ("animal", "employee")
    ordering = ("-feeding_date", "-id")
    list_per_page = 20
    actions = ("mark_done", "mark_cancelled")

    @admin.action(description="Отметить выбранные кормления выполненными")
    def mark_done(self, request, queryset):
        updated = queryset.exclude(
            status=Feeding.Status.CANCELLED,
        ).update(status=Feeding.Status.DONE)
        self.message_user(request, f"Выполнено кормлений: {updated}")

    @admin.action(description="Отменить выбранные кормления")
    def mark_cancelled(self, request, queryset):
        updated = queryset.update(status=Feeding.Status.CANCELLED)
        self.message_user(request, f"Отменено кормлений: {updated}")
