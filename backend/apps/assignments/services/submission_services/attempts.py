from __future__ import annotations

import logging
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from apps.assignments.models import Submission, SubmissionAttempt
from apps.assignments.services.submission_services.common import (
    get_assignment_policy,
    get_next_attempt_number,
)

logger = logging.getLogger(__name__)


@transaction.atomic
def create_new_submission_attempt(submission: Submission) -> Submission:
    """Создаёт новую попытку выполнения работы."""

    logger.info("create_new_submission_attempt started submission_id=%s", submission.id)

    policy = get_assignment_policy(submission.assignment)
    next_attempt_number = get_next_attempt_number(
        submission.publication,
        submission.student,
    )

    if next_attempt_number > policy.attempts_limit:
        raise ValidationError("Лимит попыток исчерпан.")

    new_submission = Submission(
        publication=submission.publication,
        assignment=submission.assignment,
        variant=submission.variant,
        student=submission.student,
        status=Submission.StatusChoices.IN_PROGRESS,
        attempt_number=next_attempt_number,
        started_at=timezone.now(),
        auto_score=Decimal("0.00"),
        manual_score=None,
        final_score=None,
        percentage=None,
        passed=None,
    )
    new_submission.full_clean()
    new_submission.save()

    attempt = SubmissionAttempt(
        submission=new_submission,
        attempt_number=next_attempt_number,
        status=SubmissionAttempt.StatusChoices.IN_PROGRESS,
        started_at=new_submission.started_at,
    )
    attempt.full_clean()
    attempt.save()

    logger.info(
        "create_new_submission_attempt completed new_submission_id=%s",
        new_submission.id,
    )
    return new_submission
