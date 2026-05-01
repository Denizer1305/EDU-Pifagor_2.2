from __future__ import annotations

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.users.models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "full_name",
        "phone",
        "city",
        "timezone",
        "created_at",
        "updated_at",
    )
    list_display_links = (
        "id",
        "user",
    )
    list_filter = (
        "gender",
        "city",
        "timezone",
        "created_at",
    )
    search_fields = (
        "user__email",
        "last_name",
        "first_name",
        "patronymic",
        "phone",
        "city",
    )
    ordering = (
        "last_name",
        "first_name",
        "patronymic",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
        "full_name",
        "short_name",
    )
    autocomplete_fields = (
        "user",
    )

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "user",
                    "last_name",
                    "first_name",
                    "patronymic",
                )
            },
        ),
        (
            _("Контактные данные"),
            {
                "fields": (
                    "phone",
                    "birth_date",
                    "gender",
                    "city",
                    "timezone",
                )
            },
        ),
        (
            _("Публичные данные"),
            {
                "fields": (
                    "avatar",
                    "about",
                    "social_link_max",
                    "social_link_vk",
                )
            },
        ),
        (
            _("Служебные поля"),
            {
                "fields": (
                    "full_name",
                    "short_name",
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related("user")
