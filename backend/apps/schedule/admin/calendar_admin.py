from __future__ import annotations

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.schedule.models import ScheduleCalendar, ScheduleWeekTemplate


@admin.register(ScheduleCalendar)
class ScheduleCalendarAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "organization",
        "academic_year",
        "education_period",
        "calendar_type",
        "starts_on",
        "ends_on",
        "is_active",
    )
    list_filter = (
        "is_active",
        "calendar_type",
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
    ordering = ("organization", "starts_on", "ends_on")
    list_select_related = (
        "organization",
        "academic_year",
        "education_period",
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
                    "academic_year",
                    "education_period",
                    "name",
                    "calendar_type",
                    "is_active",
                )
            },
        ),
        (
            _("Период"),
            {
                "fields": (
                    "starts_on",
                    "ends_on",
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


@admin.register(ScheduleWeekTemplate)
class ScheduleWeekTemplateAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "organization",
        "academic_year",
        "education_period",
        "week_type",
        "starts_on",
        "ends_on",
        "is_default",
        "is_active",
    )
    list_filter = (
        "is_active",
        "is_default",
        "week_type",
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
    ordering = ("organization", "academic_year", "week_type", "name")
    list_select_related = (
        "organization",
        "academic_year",
        "education_period",
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
                    "academic_year",
                    "education_period",
                    "name",
                    "week_type",
                    "is_default",
                    "is_active",
                )
            },
        ),
        (
            _("Период действия"),
            {
                "fields": (
                    "starts_on",
                    "ends_on",
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
