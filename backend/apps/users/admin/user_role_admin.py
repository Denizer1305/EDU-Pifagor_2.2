from __future__ import annotations

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.users.models import UserRole


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "user_email",
        "role",
        "assigned_at",
    )
    list_display_links = (
        "id",
        "user",
    )
    list_filter = (
        "role",
        "assigned_at",
    )
    search_fields = (
        "user__email",
        "role__code",
        "role__name",
    )
    ordering = (
        "-assigned_at",
    )
    readonly_fields = (
        "assigned_at",
    )
    autocomplete_fields = (
        "user",
        "role",
    )

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "user",
                    "role",
                )
            },
        ),
        (
            _("Системная информация"),
            {
                "fields": (
                    "assigned_at",
                )
            },
        ),
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related(
            "user",
            "role",
        )

    @admin.display(description=_("Email"))
    def user_email(self, obj: UserRole) -> str:
        return obj.user.email
