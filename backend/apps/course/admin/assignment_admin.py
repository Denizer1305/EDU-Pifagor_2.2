from __future__ import annotations

from django.contrib import admin

from apps.course.models import CourseAssignment


@admin.register(CourseAssignment)
class CourseAssignmentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "course",
        "assignment_type",
        "target_display",
        "assigned_by",
        "starts_at",
        "ends_at",
        "is_active",
        "auto_enroll",
        "created_at",
    )
    list_filter = (
        "assignment_type",
        "is_active",
        "auto_enroll",
        "course__organization",
        "course__subject",
        "created_at",
    )
    search_fields = (
        "course__title",
        "course__code",
        "group__name",
        "group__code",
        "student__email",
        "student__profile__last_name",
        "student__profile__first_name",
        "assigned_by__email",
    )
    autocomplete_fields = (
        "course",
        "group",
        "student",
        "assigned_by",
    )
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at")

    @admin.display(description="Кому назначен")
    def target_display(self, obj):
        if obj.group_id:
            return obj.group

        if obj.student_id:
            return obj.student

        return "—"
