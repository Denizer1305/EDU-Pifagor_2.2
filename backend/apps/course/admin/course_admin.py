from __future__ import annotations

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.course.admin.inlines import CourseModuleInline, CourseTeacherInline
from apps.course.models import Course


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "code",
        "course_type",
        "status",
        "visibility",
        "author",
        "organization",
        "subject",
        "is_template",
        "is_active",
        "published_at",
        "created_at",
    )
    list_filter = (
        "course_type",
        "origin",
        "status",
        "visibility",
        "level",
        "is_template",
        "is_active",
        "allow_self_enrollment",
        "organization",
        "subject",
        "academic_year",
        "period",
        "created_at",
    )
    search_fields = (
        "title",
        "subtitle",
        "description",
        "code",
        "slug",
        "author__email",
        "author__profile__last_name",
        "author__profile__first_name",
        "organization__name",
        "organization__short_name",
        "subject__name",
        "subject__short_name",
    )
    autocomplete_fields = (
        "author",
        "organization",
        "subject",
        "academic_year",
        "period",
        "group_subject",
    )
    readonly_fields = (
        "uid",
        "code",
        "slug",
        "published_at",
        "archived_at",
        "created_at",
        "updated_at",
    )
    ordering = ("-created_at",)
    inlines = [CourseTeacherInline, CourseModuleInline]

    fieldsets = (
        (_("Основное"), {
            "fields": (
                "uid",
                "code",
                "slug",
                "title",
                "subtitle",
                "description",
            )
        }),
        (_("Тип и публикация"), {
            "fields": (
                "course_type",
                "origin",
                "status",
                "visibility",
                "level",
                "language",
                "is_template",
                "is_active",
            )
        }),
        (_("Автор и преподаватели"), {
            "fields": (
                "author",
            )
        }),
        (_("Учебный контур"), {
            "fields": (
                "organization",
                "subject",
                "academic_year",
                "period",
                "group_subject",
            )
        }),
        (_("Доступ и оформление"), {
            "fields": (
                "cover_image",
                "allow_self_enrollment",
                "enrollment_code",
                "estimated_minutes",
            )
        }),
        (_("Даты"), {
            "fields": (
                "starts_at",
                "ends_at",
                "published_at",
                "archived_at",
            )
        }),
        (_("Служебное"), {
            "fields": (
                "created_at",
                "updated_at",
            )
        }),
    )
