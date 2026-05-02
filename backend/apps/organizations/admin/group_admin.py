from __future__ import annotations

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.organizations.admin.actions import (
    clear_group_join_code,
    disable_group_join_code,
)
from apps.organizations.models import Group


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "code",
        "organization",
        "department",
        "study_form",
        "course_number",
        "academic_year",
        "group_join_code_active_display",
        "status",
        "is_active",
        "created_at",
    )
    list_display_links = (
        "id",
        "name",
    )
    list_filter = (
        "organization",
        "department",
        "study_form",
        "status",
        "admission_year",
        "graduation_year",
        "academic_year",
        "is_active",
        "join_code_is_active",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "name",
        "code",
        "organization__name",
        "organization__short_name",
        "department__name",
        "description",
    )
    autocomplete_fields = (
        "organization",
        "department",
    )
    ordering = (
        "organization",
        "name",
    )
    readonly_fields = (
        "join_code_hash",
        "has_active_join_code_display",
        "created_at",
        "updated_at",
    )
    actions = (
        disable_group_join_code,
        clear_group_join_code,
    )

    fieldsets = (
        (
            _("Основное"),
            {
                "fields": (
                    "organization",
                    "department",
                    "name",
                    "code",
                    "description",
                )
            },
        ),
        (
            _("Учебные параметры"),
            {
                "fields": (
                    "study_form",
                    "course_number",
                    "admission_year",
                    "graduation_year",
                    "academic_year",
                    "status",
                )
            },
        ),
        (
            _("Код присоединения к группе"),
            {
                "fields": (
                    "join_code_hash",
                    "join_code_is_active",
                    "join_code_expires_at",
                    "has_active_join_code_display",
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

    @admin.display(description=_("Код группы активен"), boolean=True)
    def group_join_code_active_display(self, obj: Group) -> bool:
        return obj.has_active_join_code

    @admin.display(description=_("Есть активный код"), boolean=True)
    def has_active_join_code_display(self, obj: Group) -> bool:
        return obj.has_active_join_code
