from __future__ import annotations

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.organizations.models import SubjectCategory


@admin.register(SubjectCategory)
class SubjectCategoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "code",
        "is_active",
        "created_at",
        "updated_at",
    )
    list_display_links = (
        "id",
        "name",
    )
    list_filter = (
        "is_active",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "name",
        "code",
        "description",
    )
    ordering = ("name",)
    readonly_fields = (
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            _("Основное"),
            {
                "fields": (
                    "name",
                    "code",
                    "description",
                    "is_active",
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
