from __future__ import annotations

import logging
from decimal import ROUND_HALF_UP, Decimal

from django.db import transaction
from django.utils import timezone

from apps.assignments.models import (
    AssignmentPolicy,
    GradeRecord,
    Submission,
    SubmissionAnswer,
    SubmissionReview,
)

logger = logging.getLogger(__name__)


def _quantize(value: Decimal | int | float | None) -> Decimal | None:
    if value is None:
        return None
    return Decimal(value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _get_policy(assignment):
    policy, _ = AssignmentPolicy.objects.get_or_create(
        assignment=assignment,
        defaults={
            "check_mode": AssignmentPolicy.CheckModeChoices.MANUAL,
            "grading_mode": AssignmentPolicy.GradingModeChoices.RAW_SCORE,
            "max_score": 0,
            "passing_score": 0,
            "attempts_limit": 1,
            "allow_text_answer": True,
        },
    )
    return policy


@transaction.atomic
def recalculate_submission_answer_score(
    submission_answer: SubmissionAnswer,
) -> SubmissionAnswer:
    final_score = submission_answer.manual_score
    if final_score is None:
        final_score = submission_answer.auto_score
    if final_score is None:
        final_score = Decimal("0.00")

    submission_answer.final_score = _quantize(final_score)
    submission_answer.updated_at = timezone.now()

    submission_answer.full_clean()

    SubmissionAnswer.objects.filter(pk=submission_answer.pk).update(
        final_score=submission_answer.final_score,
        updated_at=submission_answer.updated_at,
    )

    return submission_answer


@transaction.atomic
def calculate_submission_scores(submission: Submission) -> Submission:
    logger.info("calculate_submission_scores started submission_id=%s", submission.id)

    policy = _get_policy(submission.assignment)
    answers = list(submission.answers.all())

    total_auto = Decimal("0.00")
    total_manual = Decimal("0.00")
    total_final = Decimal("0.00")

    for answer in answers:
        recalculate_submission_answer_score(answer)

        total_auto += _quantize(answer.auto_score) or Decimal("0.00")
        total_manual += _quantize(answer.manual_score) or Decimal("0.00")
        total_final += _quantize(answer.final_score) or Decimal("0.00")

    auto_score = _quantize(total_auto)
    manual_score = (
        _quantize(total_manual) if total_manual > 0 else submission.manual_score
    )
    final_score = _quantize(total_final)

    max_score = _quantize(policy.max_score) or Decimal("0.00")
    if max_score > 0:
        percentage = _quantize((final_score / max_score) * Decimal("100"))
    else:
        percentage = Decimal("0.00")

    passed = None
    if final_score is not None:
        passed = final_score >= policy.passing_score

    submission.auto_score = auto_score
    submission.manual_score = manual_score
    submission.final_score = final_score
    submission.percentage = percentage
    submission.passed = passed

    submission.full_clean()

    Submission.objects.filter(pk=submission.pk).update(
        auto_score=auto_score,
        manual_score=manual_score,
        final_score=final_score,
        percentage=percentage,
        passed=passed,
    )

    logger.info("calculate_submission_scores completed submission_id=%s", submission.id)
    return submission


@transaction.atomic
def sync_submission_review_result(review: SubmissionReview) -> Submission:
    submission = review.submission

    if review.score is not None:
        submission.manual_score = review.score
        submission.final_score = review.score

    if review.passed is not None:
        submission.passed = review.passed

    if review.reviewed_at is not None:
        submission.checked_at = review.reviewed_at

    if review.reviewer_id:
        submission.checked_by = review.reviewer

    submission.full_clean()
    submission.save()
    return submission


@transaction.atomic
def create_grade_record_from_submission(
    *,
    submission: Submission,
    graded_by=None,
    is_final: bool = True,
) -> GradeRecord:
    logger.info(
        "create_grade_record_from_submission started submission_id=%s",
        submission.id,
    )

    policy = _get_policy(submission.assignment)
    final_score = _quantize(submission.final_score) or Decimal("0.00")

    grade_value = ""
    grade_numeric = None

    if policy.grading_mode == AssignmentPolicy.GradingModeChoices.PASS_FAIL:
        grade_value = "зачёт" if submission.passed else "незачёт"
    elif policy.grading_mode == AssignmentPolicy.GradingModeChoices.FIVE_POINT:
        if submission.percentage is None:
            calculate_submission_scores(submission)
            submission.refresh_from_db()

        percentage = submission.percentage or Decimal("0.00")
        if percentage >= Decimal("85"):
            grade_numeric = Decimal("5")
        elif percentage >= Decimal("70"):
            grade_numeric = Decimal("4")
        elif percentage >= Decimal("50"):
            grade_numeric = Decimal("3")
        else:
            grade_numeric = Decimal("2")
        grade_value = str(int(grade_numeric))
    elif policy.grading_mode == AssignmentPolicy.GradingModeChoices.HUNDRED_POINT:
        grade_numeric = (
            submission.percentage if submission.percentage is not None else final_score
        )
        grade_value = str(_quantize(grade_numeric))
    elif policy.grading_mode == AssignmentPolicy.GradingModeChoices.PERCENTAGE:
        grade_numeric = (
            submission.percentage
            if submission.percentage is not None
            else Decimal("0.00")
        )
        grade_value = str(_quantize(grade_numeric))
    else:
        grade_numeric = final_score
        grade_value = str(_quantize(grade_numeric))

    grade_record = GradeRecord.objects.create(
        student=submission.student,
        assignment=submission.assignment,
        publication=submission.publication,
        submission=submission,
        grade_value=grade_value,
        grade_numeric=grade_numeric,
        grading_mode=policy.grading_mode,
        is_final=is_final,
        graded_by=graded_by or submission.checked_by,
        graded_at=submission.checked_at,
    )
    grade_record.full_clean()
    grade_record.save()

    logger.info(
        "create_grade_record_from_submission completed grade_record_id=%s",
        grade_record.id,
    )
    return grade_record
