from __future__ import annotations

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.assignments.models import (
    AssignmentAudience,
    AssignmentPublication,
)


class AssignmentAudienceInline(admin.TabularInline):
    model = AssignmentAudience
    extra = 0
    autocomplete_fields = (
        "group",
        "student",
        "course_enrollment",
    )
    fields = (
        "audience_type",
        "group",
        "student",
        "course_enrollment",
        "is_active",
    )


@admin.register(AssignmentPublication)
class AssignmentPublicationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "assignment",
        "course",
        "lesson",
        "published_by",
        "status",
        "starts_at",
        "due_at",
        "available_until",
        "is_active",
        "created_at",
    )
    list_filter = (
        "status",
        "is_active",
        "assignment__assignment_kind",
        "assignment__education_level",
        "created_at",
    )
    search_fields = (
        "assignment__title",
        "title_override",
        "notes",
        "course__title",
        "lesson__title",
        "published_by__email",
    )
    autocomplete_fields = (
        "assignment",
        "course",
        "lesson",
        "published_by",
    )
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)
    inlines = [AssignmentAudienceInline]

    fieldsets = (
        (
            _("Основное"),
            {
                "fields": (
                    "assignment",
                    "course",
                    "lesson",
                    "published_by",
                    "title_override",
                )
            },
        ),
        (
            _("Сроки"),
            {
                "fields": (
                    "starts_at",
                    "due_at",
                    "available_until",
                )
            },
        ),
        (
            _("Статус"),
            {
                "fields": (
                    "status",
                    "is_active",
                    "notes",
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


@admin.register(AssignmentAudience)
class AssignmentAudienceAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "publication",
        "audience_type",
        "group",
        "student",
        "course_enrollment",
        "is_active",
        "created_at",
    )
    list_filter = (
        "audience_type",
        "is_active",
        "publication__status",
    )
    search_fields = (
        "publication__assignment__title",
        "group__name",
        "group__code",
        "student__email",
        "student__profile__last_name",
        "student__profile__first_name",
    )
    autocomplete_fields = (
        "publication",
        "group",
        "student",
        "course_enrollment",
    )
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)
