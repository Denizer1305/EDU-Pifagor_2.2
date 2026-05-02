from __future__ import annotations

from django.contrib import admin

from apps.journal.models import AttendanceRecord


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    """Администрирование записей посещаемости."""

    list_display = (
        "id",
        "lesson",
        "student",
        "status",
        "comment",
    )
    list_filter = (
        "status",
        "lesson__date",
        "lesson__course",
        "lesson__group",
    )
    search_fields = (
        "student__email",
        "student__profile__last_name",
        "student__profile__first_name",
        "lesson__planned_topic",
        "lesson__actual_topic",
        "lesson__course__title",
        "lesson__group__name",
    )
    autocomplete_fields = (
        "lesson",
        "student",
    )
    ordering = (
        "-lesson__date",
        "lesson__lesson_number",
        "student",
    )
    list_select_related = (
        "lesson",
        "lesson__course",
        "lesson__group",
        "student",
    )
