from django.contrib import admin

from feedings.models import Feeding

from .models import Employee


class EmployeeFeedingInline(admin.TabularInline):
    """Кормления, которые провел сотрудник (только просмотр)."""

    model = Feeding
    fields = ("feeding_date", "animal", "food", "amount", "status")
    readonly_fields = fields
    extra = 0
    can_delete = False
    show_change_link = True

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "email")
    list_display_links = ("name",)
    search_fields = ("name", "email")
    ordering = ("name",)
    inlines = [EmployeeFeedingInline]
