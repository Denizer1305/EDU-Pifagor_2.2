from __future__ import annotations

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.organizations.models import TeacherSubject


@admin.register(TeacherSubject)
class TeacherSubjectAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "teacher",
        "subject",
        "is_primary",
        "is_active",
        "created_at",
        "updated_at",
    )
    list_display_links = (
        "id",
        "teacher",
    )
    list_filter = (
        "is_primary",
        "is_active",
        "subject__category",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "teacher__email",
        "teacher__profile__last_name",
        "teacher__profile__first_name",
        "subject__name",
        "subject__short_name",
        "subject__category__name",
    )
    autocomplete_fields = (
        "teacher",
        "subject",
    )
    ordering = (
        "teacher",
        "subject",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (_("Основное"), {
            "fields": (
                "teacher",
                "subject",
                "is_primary",
                "is_active",
            )
        }),
        (_("Служебное"), {
            "fields": (
                "created_at",
                "updated_at",
            )
        }),
    )
