from __future__ import annotations

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.education.admin.curriculum_inline import CurriculumItemInline
from apps.education.models import Curriculum, CurriculumItem


@admin.register(Curriculum)
class CurriculumAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "code",
        "organization",
        "department",
        "academic_year",
        "total_hours",
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
        "academic_year",
        "is_active",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "name",
        "code",
        "organization__name",
        "organization__short_name",
        "department__name",
        "department__short_name",
        "academic_year__name",
        "description",
    )
    autocomplete_fields = (
        "organization",
        "department",
        "academic_year",
    )
    ordering = (
        "organization",
        "name",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )
    list_select_related = (
        "organization",
        "department",
        "academic_year",
    )
    inlines = [CurriculumItemInline]

    fieldsets = (
        (_("Основное"), {
            "fields": (
                "organization",
                "department",
                "academic_year",
                "code",
                "name",
            )
        }),
        (_("Описание и нагрузка"), {
            "fields": (
                "description",
                "total_hours",
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


@admin.register(CurriculumItem)
class CurriculumItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "curriculum",
        "period",
        "subject",
        "sequence",
        "planned_hours",
        "contact_hours",
        "independent_hours",
        "assessment_type",
        "is_required",
        "is_active",
    )
    list_display_links = (
        "id",
        "curriculum",
    )
    list_filter = (
        "curriculum__academic_year",
        "period",
        "assessment_type",
        "is_required",
        "is_active",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "curriculum__name",
        "curriculum__code",
        "subject__name",
        "subject__short_name",
        "period__name",
        "notes",
    )
    autocomplete_fields = (
        "curriculum",
        "period",
        "subject",
    )
    ordering = (
        "curriculum",
        "period__sequence",
        "sequence",
    )
    readonly_fields = (
        "hours_balance_display",
        "created_at",
        "updated_at",
    )
    list_select_related = (
        "curriculum",
        "period",
        "subject",
        "curriculum__academic_year",
    )

    fieldsets = (
        (_("Основное"), {
            "fields": (
                "curriculum",
                "period",
                "subject",
                "sequence",
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
    def hours_balance_display(self, obj: CurriculumItem) -> int:
        return obj.planned_hours - (obj.contact_hours + obj.independent_hours)
