from __future__ import annotations

from django.contrib import admin

from apps.course.models import CourseTeacher


@admin.register(CourseTeacher)
class CourseTeacherAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "course",
        "teacher",
        "role",
        "is_active",
        "can_edit",
        "can_manage_structure",
        "can_manage_assignments",
        "assigned_at",
    )
    list_filter = (
        "role",
        "is_active",
        "can_edit",
        "can_manage_structure",
        "can_manage_assignments",
        "can_view_analytics",
        "assigned_at",
    )
    search_fields = (
        "course__title",
        "course__code",
        "teacher__email",
        "teacher__profile__last_name",
        "teacher__profile__first_name",
    )
    autocomplete_fields = (
        "course",
        "teacher",
    )
    ordering = ("course", "teacher")
    readonly_fields = (
        "assigned_at",
        "created_at",
        "updated_at",
    )
