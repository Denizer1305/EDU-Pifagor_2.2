from __future__ import annotations

from django.contrib import admin

from apps.assignments.models import (
    Rubric,
    RubricCriterion,
)


class RubricCriterionInline(admin.TabularInline):
    model = RubricCriterion
    extra = 0
    fields = (
        "title",
        "criterion_type",
        "max_score",
        "order",
        "description",
    )
    ordering = ("order", "id")


@admin.register(Rubric)
class RubricAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "assignment_kind",
        "organization",
        "author",
        "is_template",
        "is_active",
        "created_at",
    )
    list_filter = (
        "is_template",
        "is_active",
        "organization",
    )
    search_fields = (
        "title",
        "description",
        "assignment_kind",
        "author__email",
        "organization__name",
    )
    autocomplete_fields = ("organization", "author")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("title",)
    inlines = [RubricCriterionInline]


@admin.register(RubricCriterion)
class RubricCriterionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "rubric",
        "criterion_type",
        "max_score",
        "order",
        "created_at",
    )
    list_filter = ("criterion_type",)
    search_fields = (
        "title",
        "description",
        "rubric__title",
    )
    autocomplete_fields = ("rubric",)
    readonly_fields = ("created_at", "updated_at")
    ordering = ("rubric", "order", "id")
