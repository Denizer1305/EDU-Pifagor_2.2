from __future__ import annotations

from django.contrib import admin

from apps.course.models import CourseModule, CourseTeacher


class CourseTeacherInline(admin.TabularInline):
    model = CourseTeacher
    extra = 0
    autocomplete_fields = ("teacher",)
    fields = (
        "teacher",
        "role",
        "is_active",
        "can_edit",
        "can_manage_structure",
        "can_manage_assignments",
        "can_view_analytics",
        "assigned_at",
    )
    readonly_fields = ("assigned_at",)


class CourseModuleInline(admin.TabularInline):
    model = CourseModule
    extra = 0
    fields = (
        "order",
        "title",
        "is_required",
        "is_published",
        "estimated_minutes",
    )
