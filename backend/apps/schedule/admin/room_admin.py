from __future__ import annotations

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.schedule.models import ScheduleRoom


@admin.register(ScheduleRoom)
class ScheduleRoomAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "number",
        "name",
        "organization",
        "department",
        "room_type",
        "capacity",
        "building",
        "floor",
        "is_active",
    )
    list_filter = (
        "is_active",
        "room_type",
        "organization",
        "department",
        "building",
    )
    search_fields = (
        "name",
        "number",
        "building",
        "organization__name",
        "department__name",
    )
    ordering = ("organization", "building", "number", "name")
    list_select_related = (
        "organization",
        "department",
    )
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
                    "department",
                    "name",
                    "number",
                    "room_type",
                    "capacity",
                    "is_active",
                )
            },
        ),
        (
            _("Расположение"),
            {
                "fields": (
                    "building",
                    "floor",
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
