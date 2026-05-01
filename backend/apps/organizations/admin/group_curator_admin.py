from __future__ import annotations

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.organizations.models import GroupCurator


@admin.register(GroupCurator)
class GroupCuratorAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "group",
        "teacher",
        "is_primary",
        "is_active",
        "starts_at",
        "ends_at",
        "is_current_display",
        "created_at",
    )
    list_display_links = (
        "id",
        "group",
    )
    list_filter = (
        "is_primary",
        "is_active",
        "starts_at",
        "ends_at",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "group__name",
        "group__code",
        "teacher__email",
        "teacher__profile__last_name",
        "teacher__profile__first_name",
        "notes",
    )
    autocomplete_fields = (
        "group",
        "teacher",
    )
    ordering = (
        "-is_primary",
        "-is_active",
        "-starts_at",
        "-created_at",
    )
    readonly_fields = (
        "is_current_display",
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (_("Основное"), {
            "fields": (
                "group",
                "teacher",
                "is_primary",
                "is_active",
            )
        }),
        (_("Период действия"), {
            "fields": (
                "starts_at",
                "ends_at",
                "is_current_display",
            )
        }),
        (_("Примечание"), {
            "fields": (
                "notes",
            )
        }),
        (_("Служебное"), {
            "fields": (
                "created_at",
                "updated_at",
            )
        }),
    )

    @admin.display(description=_("Актуально сейчас"), boolean=True)
    def is_current_display(self, obj: GroupCurator) -> bool:
        return obj.is_current
