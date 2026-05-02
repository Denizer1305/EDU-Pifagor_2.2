from __future__ import annotations

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.organizations.models import TeacherOrganization


@admin.register(TeacherOrganization)
class TeacherOrganizationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "teacher",
        "organization",
        "position",
        "employment_type",
        "is_primary",
        "is_active",
        "starts_at",
        "ends_at",
        "is_current_display",
        "created_at",
    )
    list_display_links = (
        "id",
        "teacher",
    )
    list_filter = (
        "employment_type",
        "is_primary",
        "is_active",
        "starts_at",
        "ends_at",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "teacher__email",
        "teacher__profile__last_name",
        "teacher__profile__first_name",
        "organization__name",
        "organization__short_name",
        "position",
        "notes",
    )
    autocomplete_fields = (
        "teacher",
        "organization",
    )
    ordering = (
        "teacher",
        "organization",
    )
    readonly_fields = (
        "is_current_display",
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            _("Основное"),
            {
                "fields": (
                    "teacher",
                    "organization",
                    "position",
                    "employment_type",
                )
            },
        ),
        (
            _("Статус связи"),
            {
                "fields": (
                    "is_primary",
                    "is_active",
                    "starts_at",
                    "ends_at",
                    "is_current_display",
                )
            },
        ),
        (_("Примечание"), {"fields": ("notes",)}),
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

    @admin.display(description=_("Актуально сейчас"), boolean=True)
    def is_current_display(self, obj: TeacherOrganization) -> bool:
        return obj.is_current
