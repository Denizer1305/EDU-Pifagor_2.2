from __future__ import annotations

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.users.models import Role


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "code",
        "name",
        "description",
        "is_active",
        "created_at",
        "updated_at",
    )
    list_display_links = (
        "id",
        "code",
    )
    list_filter = (
        "is_active",
        "created_at",
    )
    search_fields = (
        "code",
        "name",
        "description",
    )
    ordering = (
        "name",
        "code",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "code",
                    "name",
                    "description",
                    "is_active",
                )
            },
        ),
        (
            _("Системная информация"),
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )
