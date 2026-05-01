from __future__ import annotations

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.organizations.models import Department


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "short_name",
        "organization",
        "is_active",
        "created_at",
        "updated_at",
    )
    list_display_links = (
        "id",
        "name",
    )
    list_filter = (
        "organization",
        "is_active",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "name",
        "short_name",
        "organization__name",
        "organization__short_name",
        "description",
    )
    autocomplete_fields = (
        "organization",
    )
    ordering = (
        "organization",
        "name",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (_("Основное"), {
            "fields": (
                "organization",
                "name",
                "short_name",
                "description",
            )
        }),
        (_("Статус"), {
            "fields": (
                "is_active",
            )
        }),
        (_("Служебное"), {
            "fields": (
                "created_at",
                "updated_at",
            )
        }),
    )
