from __future__ import annotations

from django.contrib import admin

from apps.assignments.models import (
    ReviewComment,
    SubmissionReview,
)


class ReviewCommentInline(admin.TabularInline):
    model = ReviewComment
    extra = 0
    autocomplete_fields = (
        "question",
        "submission_answer",
        "created_by",
    )
    fields = (
        "comment_type",
        "question",
        "submission_answer",
        "message",
        "score_delta",
        "created_by",
    )


@admin.register(SubmissionReview)
class SubmissionReviewAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "submission",
        "reviewer",
        "review_status",
        "score",
        "passed",
        "reviewed_at",
        "created_at",
    )
    list_filter = (
        "review_status",
        "passed",
    )
    search_fields = (
        "submission__assignment__title",
        "submission__student__email",
        "reviewer__email",
        "feedback",
        "private_note",
    )
    autocomplete_fields = ("submission", "reviewer")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)
    inlines = [ReviewCommentInline]


@admin.register(ReviewComment)
class ReviewCommentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "review",
        "comment_type",
        "question",
        "submission_answer",
        "score_delta",
        "created_by",
        "created_at",
    )
    list_filter = ("comment_type",)
    search_fields = (
        "review__submission__assignment__title",
        "message",
        "question__prompt",
    )
    autocomplete_fields = (
        "review",
        "question",
        "submission_answer",
        "created_by",
    )
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)
