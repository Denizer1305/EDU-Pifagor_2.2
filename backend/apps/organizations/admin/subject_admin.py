from __future__ import annotations

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.organizations.models import Subject


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "short_name",
        "category",
        "is_active",
        "created_at",
        "updated_at",
    )
    list_display_links = (
        "id",
        "name",
    )
    list_filter = (
        "category",
        "is_active",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "name",
        "short_name",
        "category__name",
        "category__code",
        "description",
    )
    autocomplete_fields = ("category",)
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
                    "short_name",
                    "category",
                    "description",
                )
            },
        ),
        (_("Статус"), {"fields": ("is_active",)}),
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
