from __future__ import annotations

from decimal import Decimal

from apps.assignments.models import ReviewComment, SubmissionReview
from apps.assignments.tests.factories.submission import create_submission


def create_submission_review(submission=None, reviewer=None, **kwargs):
    """Создаёт проверку сдачи."""

    submission = submission or create_submission()
    reviewer = reviewer or submission.assignment.author

    review, _ = SubmissionReview.objects.get_or_create(
        submission=submission,
        defaults={
            "reviewer": reviewer,
            "review_status": kwargs.pop("review_status", "in_progress"),
            "feedback": kwargs.pop("feedback", ""),
            "private_note": kwargs.pop("private_note", ""),
            "score": kwargs.pop("score", Decimal("0")),
            "passed": kwargs.pop("passed", False),
            "reviewed_at": kwargs.pop("reviewed_at", None),
            **kwargs,
        },
    )
    return review


def create_review_comment(review=None, created_by=None, **kwargs):
    """Создаёт комментарий проверки."""

    review = review or create_submission_review()
    created_by = created_by or review.reviewer

    return ReviewComment.objects.create(
        review=review,
        question=kwargs.pop("question", None),
        submission_answer=kwargs.pop("submission_answer", None),
        created_by=created_by,
        comment_type=kwargs.pop("comment_type", "general"),
        message=kwargs.pop("message", "Комментарий"),
        score_delta=kwargs.pop("score_delta", None),
        **kwargs,
    )
