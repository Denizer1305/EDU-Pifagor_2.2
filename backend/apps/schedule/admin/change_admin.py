from __future__ import annotations

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.schedule.models.change import ScheduleChange


@admin.register(ScheduleChange)
class ScheduleChangeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "scheduled_lesson",
        "change_type",
        "old_date",
        "new_date",
        "old_time_slot",
        "new_time_slot",
        "old_room",
        "new_room",
        "old_teacher",
        "new_teacher",
        "changed_by",
        "created_at",
    )
    list_filter = (
        "change_type",
        "old_date",
        "new_date",
        "changed_by",
    )
    search_fields = (
        "reason",
        "comment",
        "scheduled_lesson__title",
        "old_room__number",
        "new_room__number",
        "old_teacher__email",
        "new_teacher__email",
    )
    ordering = ("-created_at",)
    list_select_related = (
        "scheduled_lesson",
        "old_time_slot",
        "new_time_slot",
        "old_room",
        "new_room",
        "old_teacher",
        "new_teacher",
        "changed_by",
    )
    autocomplete_fields = (
        "scheduled_lesson",
        "old_time_slot",
        "new_time_slot",
        "old_room",
        "new_room",
        "old_teacher",
        "new_teacher",
        "changed_by",
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
                    "scheduled_lesson",
                    "change_type",
                    "reason",
                    "changed_by",
                )
            },
        ),
        (
            _("Дата и время"),
            {
                "fields": (
                    "old_date",
                    "new_date",
                    "old_time_slot",
                    "new_time_slot",
                    "old_starts_at",
                    "new_starts_at",
                    "old_ends_at",
                    "new_ends_at",
                )
            },
        ),
        (
            _("Аудитория и преподаватель"),
            {
                "fields": (
                    "old_room",
                    "new_room",
                    "old_teacher",
                    "new_teacher",
                )
            },
        ),
        (
            _("Комментарий"),
            {
                "fields": (
                    "comment",
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )
