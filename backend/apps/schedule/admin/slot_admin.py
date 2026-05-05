from __future__ import annotations

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.schedule.models import ScheduleTimeSlot


@admin.register(ScheduleTimeSlot)
class ScheduleTimeSlotAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "organization",
        "academic_year",
        "education_period",
        "number",
        "name",
        "starts_at",
        "ends_at",
        "is_active",
    )
    list_filter = (
        "is_active",
        "organization",
        "academic_year",
        "education_period",
    )
    search_fields = (
        "name",
        "organization__name",
        "academic_year__name",
        "education_period__name",
    )
    ordering = (
        "organization",
        "academic_year",
        "education_period",
        "number",
        "starts_at",
    )
    autocomplete_fields = (
        "organization",
        "academic_year",
        "education_period",
    )

    fieldsets = (
        (
            _("Основное"),
            {
                "fields": (
                    "organization",
                    "academic_year",
                    "education_period",
                    "number",
                    "name",
                    "starts_at",
                    "ends_at",
                    "is_active",
                )
            },
        ),
        (
            _("Описание"),
            {"fields": ("description",)},
        ),
    )
