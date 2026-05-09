from __future__ import annotations

from django.contrib import admin

from apps.course.models import CourseProgress, LessonProgress


@admin.register(CourseProgress)
class CourseProgressAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "course_display",
        "student_display",
        "progress_percent",
        "completed_lessons_count",
        "total_lessons_count",
        "spent_minutes",
        "last_activity_at",
        "completed_at",
    )
    list_filter = (
        "enrollment__course__organization",
        "enrollment__course__subject",
        "completed_at",
    )
    search_fields = (
        "enrollment__course__title",
        "enrollment__course__code",
        "enrollment__student__email",
        "enrollment__student__profile__last_name",
        "enrollment__student__profile__first_name",
    )
    autocomplete_fields = (
        "enrollment",
        "last_lesson",
    )
    ordering = ("-updated_at",)
    readonly_fields = ("created_at", "updated_at")

    @admin.display(description="Курс")
    def course_display(self, obj):
        return obj.enrollment.course

    @admin.display(description="Студент")
    def student_display(self, obj):
        return obj.enrollment.student


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "lesson",
        "student_display",
        "status",
        "attempts_count",
        "score",
        "spent_minutes",
        "last_viewed_at",
        "completed_at",
    )
    list_filter = (
        "status",
        "lesson__lesson_type",
        "lesson__course__organization",
        "lesson__course__subject",
    )
    search_fields = (
        "lesson__title",
        "lesson__module__title",
        "lesson__course__title",
        "enrollment__student__email",
        "enrollment__student__profile__last_name",
        "enrollment__student__profile__first_name",
    )
    autocomplete_fields = (
        "enrollment",
        "course_progress",
        "lesson",
    )
    ordering = ("lesson", "id")
    readonly_fields = ("created_at", "updated_at")

    @admin.display(description="Студент")
    def student_display(self, obj):
        return obj.enrollment.student
