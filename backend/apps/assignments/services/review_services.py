from __future__ import annotations

import logging

from django.db import transaction
from django.utils import timezone

from apps.assignments.models import (
    ReviewComment,
    Submission,
    SubmissionAnswer,
    SubmissionReview,
)

logger = logging.getLogger(__name__)


@transaction.atomic
def start_submission_review(
    *,
    submission: Submission,
    reviewer,
) -> SubmissionReview:
    logger.info(
        "start_submission_review started submission_id=%s reviewer_id=%s",
        submission.id,
        getattr(reviewer, "id", None),
    )

    review, _ = SubmissionReview.objects.get_or_create(
        submission=submission,
        defaults={
            "reviewer": reviewer,
            "review_status": SubmissionReview.ReviewStatusChoices.IN_REVIEW,
        },
    )

    review.reviewer = reviewer
    review.review_status = SubmissionReview.ReviewStatusChoices.IN_REVIEW
    review.full_clean()
    review.save()

    submission.status = Submission.StatusChoices.UNDER_REVIEW
    submission.checked_by = reviewer
    submission.full_clean()
    submission.save()

    return review


@transaction.atomic
def review_submission_answer(
    *,
    submission_answer: SubmissionAnswer,
    reviewer,
    manual_score=None,
    is_correct=None,
    review_status: str = SubmissionAnswer.ReviewStatusChoices.REVIEWED,
) -> SubmissionAnswer:
    start_submission_review(
        submission=submission_answer.submission,
        reviewer=reviewer,
    )

    if manual_score is not None:
        submission_answer.manual_score = manual_score

    if is_correct is not None:
        submission_answer.is_correct = is_correct

    if submission_answer.manual_score is not None:
        submission_answer.final_score = submission_answer.manual_score
    elif submission_answer.auto_score is not None:
        submission_answer.final_score = submission_answer.auto_score

    submission_answer.review_status = review_status
    submission_answer.full_clean()
    submission_answer.save()

    return submission_answer


@transaction.atomic
def add_review_comment(
    *,
    review: SubmissionReview,
    message: str,
    created_by,
    comment_type: str = ReviewComment.CommentTypeChoices.GENERAL,
    question=None,
    submission_answer=None,
    score_delta=None,
) -> ReviewComment:
    comment = ReviewComment(
        review=review,
        question=question,
        submission_answer=submission_answer,
        comment_type=comment_type,
        message=message,
        score_delta=score_delta,
        created_by=created_by,
    )
    comment.full_clean()
    comment.save()
    return comment


@transaction.atomic
def submit_submission_review(
    *,
    review: SubmissionReview,
    reviewer,
    feedback: str = "",
    private_note: str = "",
    score=None,
    passed=None,
) -> SubmissionReview:
    logger.info("submit_submission_review started review_id=%s", review.id)

    review.reviewer = reviewer
    review.feedback = feedback
    review.private_note = private_note
    review.score = score
    review.passed = passed
    review.review_status = SubmissionReview.ReviewStatusChoices.REVIEWED
    review.reviewed_at = timezone.now()
    review.full_clean()
    review.save()

    submission = review.submission
    submission.status = Submission.StatusChoices.REVIEWED
    submission.checked_at = review.reviewed_at
    submission.checked_by = reviewer
    if score is not None:
        submission.manual_score = score
        submission.final_score = score
    if passed is not None:
        submission.passed = passed
    submission.full_clean()
    submission.save()

    logger.info("submit_submission_review completed review_id=%s", review.id)
    return review


@transaction.atomic
def return_submission_for_revision(
    *,
    review: SubmissionReview,
    reviewer,
    feedback: str = "",
    private_note: str = "",
) -> SubmissionReview:
    review.reviewer = reviewer
    review.feedback = feedback
    review.private_note = private_note
    review.review_status = SubmissionReview.ReviewStatusChoices.RETURNED
    review.reviewed_at = timezone.now()
    review.full_clean()
    review.save()

    submission = review.submission
    submission.status = Submission.StatusChoices.RETURNED_FOR_REVISION
    submission.checked_at = review.reviewed_at
    submission.checked_by = reviewer
    submission.full_clean()
    submission.save()

    return review


@transaction.atomic
def approve_submission_review(
    *,
    review: SubmissionReview,
    reviewer,
    score=None,
    feedback: str = "",
) -> SubmissionReview:
    review.reviewer = reviewer
    review.feedback = feedback or review.feedback
    review.score = score if score is not None else review.score
    review.passed = True
    review.review_status = SubmissionReview.ReviewStatusChoices.APPROVED
    review.reviewed_at = timezone.now()
    review.full_clean()
    review.save()

    submission = review.submission
    submission.status = Submission.StatusChoices.ACCEPTED
    submission.checked_at = review.reviewed_at
    submission.checked_by = reviewer
    submission.passed = True
    if review.score is not None:
        submission.manual_score = review.score
        submission.final_score = review.score
    submission.full_clean()
    submission.save()

    return review


@transaction.atomic
def reject_submission_review(
    *,
    review: SubmissionReview,
    reviewer,
    score=None,
    feedback: str = "",
) -> SubmissionReview:
    review.reviewer = reviewer
    review.feedback = feedback or review.feedback
    review.score = score if score is not None else review.score
    review.passed = False
    review.review_status = SubmissionReview.ReviewStatusChoices.REJECTED
    review.reviewed_at = timezone.now()
    review.full_clean()
    review.save()

    submission = review.submission
    submission.status = Submission.StatusChoices.REJECTED
    submission.checked_at = review.reviewed_at
    submission.checked_by = reviewer
    submission.passed = False
    if review.score is not None:
        submission.manual_score = review.score
        submission.final_score = review.score
    submission.full_clean()
    submission.save()

    return review
