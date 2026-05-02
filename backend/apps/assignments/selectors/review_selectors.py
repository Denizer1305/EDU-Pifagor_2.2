from __future__ import annotations

from django.db.models import Q, QuerySet

from apps.assignments.models import ReviewComment, SubmissionReview


def get_submission_review_base_queryset() -> QuerySet[SubmissionReview]:
    return SubmissionReview.objects.select_related(
        "submission",
        "submission__assignment",
        "submission__student",
        "reviewer",
    ).order_by("-created_at")


def get_submission_reviews_queryset(
    *,
    search: str = "",
    review_status: str = "",
    reviewer_id: int | None = None,
    submission_id: int | None = None,
) -> QuerySet[SubmissionReview]:
    queryset = get_submission_review_base_queryset()

    if search:
        queryset = queryset.filter(
            Q(submission__assignment__title__icontains=search)
            | Q(submission__student__email__icontains=search)
            | Q(submission__student__profile__last_name__icontains=search)
            | Q(submission__student__profile__first_name__icontains=search)
            | Q(reviewer__email__icontains=search)
            | Q(feedback__icontains=search)
            | Q(private_note__icontains=search)
        )

    if review_status:
        queryset = queryset.filter(review_status=review_status)

    if reviewer_id:
        queryset = queryset.filter(reviewer_id=reviewer_id)

    if submission_id:
        queryset = queryset.filter(submission_id=submission_id)

    return queryset


def get_submission_review_by_id(*, review_id: int) -> SubmissionReview | None:
    return (
        get_submission_review_base_queryset()
        .prefetch_related(
            "comments__question",
            "comments__submission_answer",
            "comments__created_by",
        )
        .filter(id=review_id)
        .first()
    )


def get_review_comments_queryset(
    *,
    review_id: int | None = None,
    comment_type: str = "",
    question_id: int | None = None,
    submission_answer_id: int | None = None,
) -> QuerySet[ReviewComment]:
    queryset = ReviewComment.objects.select_related(
        "review",
        "question",
        "submission_answer",
        "created_by",
    ).order_by("-created_at")

    if review_id:
        queryset = queryset.filter(review_id=review_id)

    if comment_type:
        queryset = queryset.filter(comment_type=comment_type)

    if question_id:
        queryset = queryset.filter(question_id=question_id)

    if submission_answer_id:
        queryset = queryset.filter(submission_answer_id=submission_answer_id)

    return queryset
