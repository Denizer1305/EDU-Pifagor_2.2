from __future__ import annotations

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.education.models import GroupSubject


@admin.register(GroupSubject)
class GroupSubjectAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "group",
        "subject",
        "academic_year",
        "period",
        "planned_hours",
        "contact_hours",
        "independent_hours",
        "assessment_type",
        "is_required",
        "is_active",
    )
    list_display_links = (
        "id",
        "group",
    )
    list_filter = (
        "academic_year",
        "period",
        "assessment_type",
        "is_required",
        "is_active",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "group__name",
        "group__code",
        "subject__name",
        "subject__short_name",
        "academic_year__name",
        "period__name",
        "notes",
    )
    autocomplete_fields = (
        "group",
        "subject",
        "academic_year",
        "period",
    )
    ordering = (
        "group",
        "period__sequence",
        "subject",
    )
    readonly_fields = (
        "hours_balance_display",
        "created_at",
        "updated_at",
    )
    list_select_related = (
        "group",
        "subject",
        "academic_year",
        "period",
    )

    fieldsets = (
        (_("Основное"), {
            "fields": (
                "group",
                "subject",
                "academic_year",
                "period",
            )
        }),
        (_("Нагрузка"), {
            "fields": (
                "planned_hours",
                "contact_hours",
                "independent_hours",
                "hours_balance_display",
            )
        }),
        (_("Аттестация и статус"), {
            "fields": (
                "assessment_type",
                "is_required",
                "is_active",
            )
        }),
        (_("Дополнительно"), {
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

    @admin.display(description=_("Остаток часов"))
    def hours_balance_display(self, obj: GroupSubject) -> int:
        return obj.planned_hours - (obj.contact_hours + obj.independent_hours)
