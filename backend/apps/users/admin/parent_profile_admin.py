from __future__ import annotations

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.users.admin.helpers import get_user_full_name_or_email
from apps.users.models import ParentProfile


@admin.register(ParentProfile)
class ParentProfileAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "full_name_display",
        "work_place",
        "created_at",
        "updated_at",
    )
    list_display_links = (
        "id",
        "user",
    )
    search_fields = (
        "user__email",
        "user__profile__last_name",
        "user__profile__first_name",
        "work_place",
    )
    ordering = (
        "user__profile__last_name",
        "user__profile__first_name",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
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
                    "work_place",
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

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related(
            "user",
            "user__profile",
        )

    @admin.display(description=_("ФИО"))
    def full_name_display(self, obj: ParentProfile) -> str:
        return get_user_full_name_or_email(obj.user)
