from __future__ import annotations

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.organizations.admin.actions import (
    clear_teacher_registration_code,
    disable_teacher_registration_code,
)
from apps.organizations.models import Organization


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "short_name",
        "type",
        "city",
        "email",
        "teacher_code_active_display",
        "teacher_registration_code_expires_at",
        "is_active",
        "created_at",
    )
    list_display_links = (
        "id",
        "name",
    )
    list_filter = (
        "type",
        "city",
        "is_active",
        "teacher_registration_code_is_active",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "name",
        "short_name",
        "city",
        "email",
        "phone",
        "address",
        "website",
    )
    autocomplete_fields = (
        "type",
    )
    ordering = (
        "name",
    )
    readonly_fields = (
        "teacher_registration_code_hash",
        "has_active_teacher_registration_code_display",
        "created_at",
        "updated_at",
    )
    actions = (
        disable_teacher_registration_code,
        clear_teacher_registration_code,
    )

    fieldsets = (
        (_("Основное"), {
            "fields": (
                "name",
                "short_name",
                "type",
                "description",
            )
        }),
        (_("Контактные данные"), {
            "fields": (
                "city",
                "address",
                "phone",
                "email",
                "website",
            )
        }),
        (_("Логотип"), {
            "fields": (
                "logo",
            )
        }),
        (_("Код регистрации преподавателя"), {
            "fields": (
                "teacher_registration_code_hash",
                "teacher_registration_code_is_active",
                "teacher_registration_code_expires_at",
                "has_active_teacher_registration_code_display",
            )
        }),
        (_("Статус"), {
            "fields": (
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

    @admin.display(description=_("Код преподавателя активен"), boolean=True)
    def teacher_code_active_display(self, obj: Organization) -> bool:
        return obj.has_active_teacher_registration_code

    @admin.display(description=_("Есть активный код"), boolean=True)
    def has_active_teacher_registration_code_display(self, obj: Organization) -> bool:
        return obj.has_active_teacher_registration_code
