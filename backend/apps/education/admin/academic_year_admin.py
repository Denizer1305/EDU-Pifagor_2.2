from __future__ import annotations

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.education.models import AcademicYear


@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "start_date",
        "end_date",
        "is_current",
        "is_active",
        "created_at",
    )
    list_display_links = (
        "id",
        "name",
    )
    list_filter = (
        "is_current",
        "is_active",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "name",
        "description",
    )
    ordering = ("-start_date",)
    readonly_fields = (
        "created_at",
        "updated_at",
    )
    date_hierarchy = "start_date"

    fieldsets = (
        (
            _("Основное"),
            {
                "fields": (
                    "name",
                    "start_date",
                    "end_date",
                    "description",
                )
            },
        ),
        (
            _("Статус"),
            {
                "fields": (
                    "is_current",
                    "is_active",
                )
            },
        ),
        (
            _("Служебное"),
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )
