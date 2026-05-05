from __future__ import annotations

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.schedule.models import ScheduleTimeSlot


@admin.register(ScheduleTimeSlot)
class ScheduleTimeSlotAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "organization",
        "number",
        "name",
        "starts_at",
        "ends_at",
        "duration_minutes",
        "education_level",
        "is_pair",
        "is_active",
    )
    list_filter = (
        "is_active",
        "is_pair",
        "education_level",
        "organization",
    )
    search_fields = (
        "name",
        "organization__name",
    )
    ordering = ("organization", "education_level", "number", "starts_at")
    list_select_related = ("organization",)
    readonly_fields = (
        "created_at",
        "updated_at",
    )
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "organization",
                    "name",
                    "number",
                    "education_level",
                    "is_pair",
                    "is_active",
                )
            },
        ),
        (
            _("Время"),
            {
                "fields": (
                    "starts_at",
                    "ends_at",
                    "duration_minutes",
                )
            },
        ),
        (
            _("Дополнительно"),
            {
                "fields": (
                    "notes",
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )
