from __future__ import annotations

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.assignments.models import (
    Submission,
    SubmissionAnswer,
    SubmissionAttachment,
    SubmissionAttempt,
)


class SubmissionAnswerInline(admin.TabularInline):
    model = SubmissionAnswer
    extra = 0
    autocomplete_fields = ("question",)
    fields = (
        "question",
        "is_correct",
        "auto_score",
        "manual_score",
        "final_score",
        "review_status",
    )


class SubmissionAttachmentInline(admin.TabularInline):
    model = SubmissionAttachment
    extra = 0
    autocomplete_fields = ("question",)
    fields = (
        "question",
        "file",
        "attachment_type",
        "original_name",
        "file_size",
    )
    readonly_fields = ("original_name", "mime_type", "file_size")


class SubmissionAttemptInline(admin.TabularInline):
    model = SubmissionAttempt
    extra = 0
    fields = (
        "attempt_number",
        "status",
        "started_at",
        "submitted_at",
        "time_spent_minutes",
    )
    readonly_fields = ("started_at", "submitted_at")


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "assignment",
        "publication",
        "student",
        "variant",
        "status",
        "attempt_number",
        "final_score",
        "percentage",
        "passed",
        "is_late",
        "submitted_at",
        "checked_at",
    )
    list_filter = (
        "status",
        "passed",
        "is_late",
        "assignment__assignment_kind",
        "publication__status",
        "created_at",
    )
    search_fields = (
        "assignment__title",
        "student__email",
        "student__profile__last_name",
        "student__profile__first_name",
        "publication__assignment__title",
    )
    autocomplete_fields = (
        "publication",
        "assignment",
        "variant",
        "student",
        "checked_by",
    )
    readonly_fields = (
        "submitted_at",
        "completed_at",
        "is_late",
        "late_minutes",
        "created_at",
        "updated_at",
    )
    ordering = ("-created_at",)
    inlines = [
        SubmissionAnswerInline,
        SubmissionAttachmentInline,
        SubmissionAttemptInline,
    ]

    fieldsets = (
        (
            _("Основное"),
            {
                "fields": (
                    "publication",
                    "assignment",
                    "variant",
                    "student",
                    "status",
                    "attempt_number",
                )
            },
        ),
        (
            _("Сроки и время"),
            {
                "fields": (
                    "started_at",
                    "submitted_at",
                    "completed_at",
                    "time_spent_minutes",
                    "is_late",
                    "late_minutes",
                )
            },
        ),
        (
            _("Оценивание"),
            {
                "fields": (
                    "auto_score",
                    "manual_score",
                    "final_score",
                    "percentage",
                    "passed",
                )
            },
        ),
        (
            _("Проверка"),
            {
                "fields": (
                    "checked_at",
                    "checked_by",
                )
            },
        ),
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


@admin.register(SubmissionAnswer)
class SubmissionAnswerAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "submission",
        "question",
        "is_correct",
        "auto_score",
        "manual_score",
        "final_score",
        "review_status",
        "created_at",
    )
    list_filter = (
        "is_correct",
        "review_status",
        "question__question_type",
    )
    search_fields = (
        "submission__assignment__title",
        "submission__student__email",
        "question__prompt",
        "answer_text",
    )
    autocomplete_fields = ("submission", "question")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)


@admin.register(SubmissionAttachment)
class SubmissionAttachmentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "submission",
        "question",
        "attachment_type",
        "original_name",
        "file_size",
        "created_at",
    )
    list_filter = ("attachment_type",)
    search_fields = (
        "submission__assignment__title",
        "submission__student__email",
        "original_name",
    )
    autocomplete_fields = ("submission", "question")
    readonly_fields = (
        "original_name",
        "mime_type",
        "file_size",
        "created_at",
        "updated_at",
    )
    ordering = ("-created_at",)


@admin.register(SubmissionAttempt)
class SubmissionAttemptAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "submission",
        "attempt_number",
        "status",
        "started_at",
        "submitted_at",
        "time_spent_minutes",
        "created_at",
    )
    list_filter = ("status",)
    search_fields = (
        "submission__assignment__title",
        "submission__student__email",
    )
    autocomplete_fields = ("submission",)
    readonly_fields = ("created_at", "updated_at")
    ordering = ("submission", "attempt_number")
