from __future__ import annotations

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.course.models import CourseLesson, CourseMaterial, CourseModule


@admin.register(CourseModule)
class CourseModuleAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "course",
        "order",
        "is_required",
        "is_published",
        "estimated_minutes",
        "created_at",
    )
    list_filter = (
        "is_required",
        "is_published",
        "course__organization",
        "course__subject",
        "created_at",
    )
    search_fields = (
        "title",
        "description",
        "course__title",
        "course__code",
    )
    autocomplete_fields = ("course",)
    ordering = ("course", "order")
    readonly_fields = ("created_at", "updated_at")


@admin.register(CourseLesson)
class CourseLessonAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "course",
        "module",
        "lesson_type",
        "order",
        "is_required",
        "is_preview",
        "is_published",
        "estimated_minutes",
    )
    list_filter = (
        "lesson_type",
        "is_required",
        "is_preview",
        "is_published",
        "course__organization",
        "course__subject",
    )
    search_fields = (
        "title",
        "subtitle",
        "description",
        "content",
        "course__title",
        "module__title",
    )
    autocomplete_fields = (
        "course",
        "module",
    )
    ordering = ("module", "order")
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        (
            _("Основное"),
            {
                "fields": (
                    "course",
                    "module",
                    "order",
                    "title",
                    "subtitle",
                    "description",
                    "lesson_type",
                )
            },
        ),
        (
            _("Контент"),
            {
                "fields": (
                    "content",
                    "video_url",
                    "external_url",
                )
            },
        ),
        (
            _("Доступ"),
            {
                "fields": (
                    "estimated_minutes",
                    "is_required",
                    "is_preview",
                    "is_published",
                    "available_from",
                )
            },
        ),
        (
            _("Служебное"),
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )


@admin.register(CourseMaterial)
class CourseMaterialAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "material_type",
        "course",
        "lesson",
        "order",
        "is_visible",
        "is_downloadable",
        "created_at",
    )
    list_filter = (
        "material_type",
        "is_visible",
        "is_downloadable",
        "course__organization",
        "course__subject",
    )
    search_fields = (
        "title",
        "description",
        "course__title",
        "lesson__title",
    )
    autocomplete_fields = (
        "course",
        "lesson",
    )
    ordering = ("course", "lesson", "order")
    readonly_fields = ("created_at", "updated_at")
