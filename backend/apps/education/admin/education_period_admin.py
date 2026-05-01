from __future__ import annotations

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.education.models import EducationPeriod


@admin.register(EducationPeriod)
class EducationPeriodAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "code",
        "academic_year",
        "period_type",
        "sequence",
        "start_date",
        "end_date",
        "is_current",
        "is_active",
    )
    list_display_links = (
        "id",
        "name",
    )
    list_filter = (
        "academic_year",
        "period_type",
        "is_current",
        "is_active",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "name",
        "code",
        "academic_year__name",
        "description",
    )
    autocomplete_fields = (
        "academic_year",
    )
    ordering = (
        "academic_year",
        "sequence",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )
    list_select_related = (
        "academic_year",
    )
    date_hierarchy = "start_date"

    fieldsets = (
        (_("Основное"), {
            "fields": (
                "academic_year",
                "name",
                "code",
                "period_type",
                "sequence",
            )
        }),
        (_("Даты"), {
            "fields": (
                "start_date",
                "end_date",
            )
        }),
        (_("Описание и статус"), {
            "fields": (
                "description",
                "is_current",
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
