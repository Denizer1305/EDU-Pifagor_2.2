from __future__ import annotations

from django.contrib import admin

from apps.journal.admin.forms import JournalGradeAdminForm
from apps.journal.models import AttendanceRecord, JournalGrade


class AttendanceInline(admin.TabularInline):
    """Посещаемость студентов прямо в карточке занятия."""

    model = AttendanceRecord
    extra = 0
    show_change_link = True
    fields = (
        "student",
        "status",
        "comment",
    )
    autocomplete_fields = ("student",)


class GradeInline(admin.TabularInline):
    """Оценки студентов прямо в карточке занятия."""

    model = JournalGrade
    form = JournalGradeAdminForm
    extra = 0
    show_change_link = True
    fields = (
        "student",
        "grade_type",
        "scale",
        "score_five",
        "is_passed",
        "weight",
        "is_auto",
        "graded_by",
        "comment",
    )
    readonly_fields = ("is_auto",)
    autocomplete_fields = (
        "student",
        "graded_by",
    )
