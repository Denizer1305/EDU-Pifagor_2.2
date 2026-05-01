from __future__ import annotations

from django.contrib import admin

from apps.education.models import CurriculumItem


class CurriculumItemInline(admin.TabularInline):
    model = CurriculumItem
    extra = 0
    autocomplete_fields = (
        "period",
        "subject",
    )
    fields = (
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
    ordering = (
        "period__sequence",
        "sequence",
    )
    show_change_link = True
