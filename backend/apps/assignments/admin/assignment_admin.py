from __future__ import annotations

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.assignments.admin.structure_admin import (
    AssignmentAttachmentInline,
    AssignmentSectionInline,
    AssignmentVariantInline,
)
from apps.assignments.models import (
    Assignment,
    AssignmentOfficialFormat,
    AssignmentPolicy,
)


class AssignmentPolicyInline(admin.StackedInline):
    model = AssignmentPolicy
    extra = 0
    can_delete = False
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (_("Проверка и оценивание"), {
            "fields": (
                "check_mode",
                "grading_mode",
                "max_score",
                "passing_score",
                "requires_manual_review",
            )
        }),
        (_("Попытки и время"), {
            "fields": (
                "attempts_limit",
                "time_limit_minutes",
                "recommended_time_minutes",
                "auto_submit_on_timeout",
            )
        }),
        (_("Отображение и поведение"), {
            "fields": (
                "shuffle_questions",
                "shuffle_answers",
                "show_results_immediately",
                "show_correct_answers_after_submit",
            )
        }),
        (_("Сдача"), {
            "fields": (
                "allow_late_submission",
                "late_penalty_percent",
                "allow_file_upload",
                "allow_text_answer",
                "allow_photo_upload",
            )
        }),
        (_("Служебное"), {
            "fields": (
                "created_at",
                "updated_at",
            )
        }),
    )


class AssignmentOfficialFormatInline(admin.StackedInline):
    model = AssignmentOfficialFormat
    extra = 0
    can_delete = False
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (_("Официальный формат"), {
            "fields": (
                "official_family",
                "assessment_year",
                "grade_level",
                "exam_subject_name",
                "is_preparation_only",
            )
        }),
        (_("Источник"), {
            "fields": (
                "source_kind",
                "source_title",
                "source_url",
                "format_version",
            )
        }),
        (_("Дополнительно"), {
            "fields": (
                "has_answer_key",
                "has_scoring_criteria",
                "has_official_demo_source",
            )
        }),
        (_("Служебное"), {
            "fields": (
                "created_at",
                "updated_at",
            )
        }),
    )


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "assignment_kind",
        "control_scope",
        "education_level",
        "status",
        "visibility",
        "course",
        "lesson",
        "author",
        "is_template",
        "is_active",
        "published_at",
        "created_at",
    )
    list_filter = (
        "assignment_kind",
        "control_scope",
        "education_level",
        "status",
        "visibility",
        "is_template",
        "is_active",
        "organization",
        "subject",
        "created_at",
    )
    search_fields = (
        "title",
        "subtitle",
        "description",
        "instructions",
        "author__email",
        "author__profile__last_name",
        "author__profile__first_name",
        "course__title",
        "lesson__title",
        "subject__name",
        "organization__name",
    )
    autocomplete_fields = (
        "course",
        "lesson",
        "subject",
        "organization",
        "author",
    )
    readonly_fields = (
        "uid",
        "published_at",
        "archived_at",
        "created_at",
        "updated_at",
    )
    ordering = ("-created_at",)
    inlines = [
        AssignmentPolicyInline,
        AssignmentOfficialFormatInline,
        AssignmentVariantInline,
        AssignmentSectionInline,
        AssignmentAttachmentInline,
    ]

    fieldsets = (
        (_("Основное"), {
            "fields": (
                "uid",
                "title",
                "subtitle",
                "description",
                "instructions",
            )
        }),
        (_("Связи"), {
            "fields": (
                "course",
                "lesson",
                "subject",
                "organization",
                "author",
            )
        }),
        (_("Классификация"), {
            "fields": (
                "assignment_kind",
                "control_scope",
                "education_level",
            )
        }),
        (_("Статус и видимость"), {
            "fields": (
                "status",
                "visibility",
                "is_template",
                "is_active",
            )
        }),
        (_("Служебное"), {
            "fields": (
                "published_at",
                "archived_at",
                "created_at",
                "updated_at",
            )
        }),
    )
