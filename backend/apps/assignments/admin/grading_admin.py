from __future__ import annotations

from django.contrib import admin

from apps.assignments.models import (
    Appeal,
    GradeRecord,
    PlagiarismCheck,
)


@admin.register(GradeRecord)
class GradeRecordAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "student",
        "assignment",
        "publication",
        "submission",
        "grade_value",
        "grade_numeric",
        "grading_mode",
        "is_final",
        "graded_by",
        "graded_at",
    )
    list_filter = (
        "grading_mode",
        "is_final",
        "graded_at",
    )
    search_fields = (
        "student__email",
        "student__profile__last_name",
        "student__profile__first_name",
        "assignment__title",
        "grade_value",
    )
    autocomplete_fields = (
        "student",
        "assignment",
        "publication",
        "submission",
        "graded_by",
    )
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-graded_at", "-created_at")


@admin.register(PlagiarismCheck)
class PlagiarismCheckAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "submission",
        "status",
        "similarity_percent",
        "checked_at",
        "created_at",
    )
    list_filter = ("status",)
    search_fields = (
        "submission__assignment__title",
        "submission__student__email",
        "report_url",
    )
    autocomplete_fields = ("submission",)
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)


@admin.register(Appeal)
class AppealAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "submission",
        "student",
        "status",
        "resolved_by",
        "resolved_at",
        "created_at",
    )
    list_filter = (
        "status",
        "resolved_at",
    )
    search_fields = (
        "submission__assignment__title",
        "student__email",
        "student__profile__last_name",
        "student__profile__first_name",
        "reason",
        "resolution",
    )
    autocomplete_fields = (
        "submission",
        "student",
        "resolved_by",
    )
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)
