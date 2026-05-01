from __future__ import annotations

from django.contrib import admin

from apps.course.models import CourseEnrollment


@admin.register(CourseEnrollment)
class CourseEnrollmentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "course",
        "student",
        "status",
        "progress_percent",
        "enrolled_at",
        "started_at",
        "completed_at",
        "last_activity_at",
    )
    list_filter = (
        "status",
        "course__organization",
        "course__subject",
        "enrolled_at",
    )
    search_fields = (
        "course__title",
        "course__code",
        "student__email",
        "student__profile__last_name",
        "student__profile__first_name",
    )
    autocomplete_fields = (
        "course",
        "student",
        "assignment",
    )
    ordering = ("-enrolled_at",)
    readonly_fields = ("created_at", "updated_at")
