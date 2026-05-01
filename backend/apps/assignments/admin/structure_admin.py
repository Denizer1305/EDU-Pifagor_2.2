from __future__ import annotations

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.assignments.models import (
    AssignmentAttachment,
    AssignmentQuestion,
    AssignmentSection,
    AssignmentVariant,
)


class AssignmentVariantInline(admin.TabularInline):
    model = AssignmentVariant
    extra = 0
    fields = (
        "title",
        "code",
        "variant_number",
        "order",
        "is_default",
        "max_score",
        "is_active",
    )
    ordering = ("order", "variant_number", "id")


class AssignmentSectionInline(admin.TabularInline):
    model = AssignmentSection
    extra = 0
    fields = (
        "title",
        "variant",
        "section_type",
        "order",
        "max_score",
        "is_required",
    )
    autocomplete_fields = ("variant",)
    ordering = ("order", "id")


class AssignmentAttachmentInline(admin.TabularInline):
    model = AssignmentAttachment
    extra = 0
    fields = (
        "title",
        "variant",
        "attachment_type",
        "file",
        "external_url",
        "is_visible_to_students",
        "order",
    )
    autocomplete_fields = ("variant",)
    ordering = ("order", "id")


@admin.register(AssignmentVariant)
class AssignmentVariantAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "assignment",
        "variant_number",
        "order",
        "is_default",
        "max_score",
        "is_active",
        "created_at",
    )
    list_filter = (
        "is_default",
        "is_active",
        "assignment__assignment_kind",
        "assignment__education_level",
    )
    search_fields = (
        "title",
        "code",
        "description",
        "assignment__title",
    )
    autocomplete_fields = ("assignment",)
    readonly_fields = ("created_at", "updated_at")
    ordering = ("assignment", "order", "variant_number", "id")


@admin.register(AssignmentSection)
class AssignmentSectionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "assignment",
        "variant",
        "section_type",
        "order",
        "max_score",
        "is_required",
        "created_at",
    )
    list_filter = (
        "section_type",
        "is_required",
        "assignment__assignment_kind",
    )
    search_fields = (
        "title",
        "description",
        "assignment__title",
        "variant__title",
    )
    autocomplete_fields = ("assignment", "variant")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("assignment", "order", "id")


@admin.register(AssignmentQuestion)
class AssignmentQuestionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "assignment",
        "variant",
        "section",
        "question_type",
        "short_prompt",
        "order",
        "max_score",
        "is_required",
        "requires_manual_review",
        "created_at",
    )
    list_filter = (
        "question_type",
        "is_required",
        "requires_manual_review",
        "assignment__assignment_kind",
        "assignment__education_level",
    )
    search_fields = (
        "prompt",
        "description",
        "explanation",
        "assignment__title",
        "variant__title",
        "section__title",
    )
    autocomplete_fields = ("assignment", "variant", "section")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("assignment", "order", "id")

    @admin.display(description=_("Формулировка"))
    def short_prompt(self, obj):
        return (obj.prompt[:80] + "...") if len(obj.prompt) > 80 else obj.prompt


@admin.register(AssignmentAttachment)
class AssignmentAttachmentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "assignment",
        "variant",
        "attachment_type",
        "is_visible_to_students",
        "order",
        "created_at",
    )
    list_filter = (
        "attachment_type",
        "is_visible_to_students",
        "assignment__assignment_kind",
    )
    search_fields = (
        "title",
        "assignment__title",
        "variant__title",
    )
    autocomplete_fields = ("assignment", "variant")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("assignment", "order", "id")
