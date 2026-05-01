from __future__ import annotations

import logging

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from apps.assignments.models import Submission, SubmissionAttempt
from apps.assignments.services.submission_services.availability import is_student_assigned
from apps.assignments.services.submission_services.common import (
    get_assignment_policy,
    get_next_attempt_number,
)

logger = logging.getLogger(__name__)


@transaction.atomic
def start_submission(
    *,
    publication,
    student,
    variant=None,
) -> Submission:
    """Начинает выполнение опубликованной работы студентом."""

    logger.info(
        "start_submission started publication_id=%s student_id=%s",
        publication.id,
        student.id,
    )

    if publication.status not in {
        publication.StatusChoices.PUBLISHED,
        publication.StatusChoices.SCHEDULED,
    }:
        raise ValidationError("Нельзя начать выполнение по неопубликованной публикации.")

    if publication.starts_at and timezone.now() < publication.starts_at:
        raise ValidationError("Работа ещё недоступна для выполнения.")

    if publication.available_until and timezone.now() > publication.available_until:
        raise ValidationError("Срок доступа к работе уже истёк.")

    if not is_student_assigned(publication, student):
        raise ValidationError("Эта работа не назначена данному студенту.")

    policy = get_assignment_policy(publication.assignment)

    existing_draft = Submission.objects.filter(
        publication=publication,
        student=student,
        status__in=(
            Submission.StatusChoices.DRAFT,
            Submission.StatusChoices.IN_PROGRESS,
            Submission.StatusChoices.RETURNED_FOR_REVISION,
        ),
    ).order_by("-attempt_number", "-id").first()

    if existing_draft:
        return existing_draft

    next_attempt_number = get_next_attempt_number(publication, student)

    if next_attempt_number > policy.attempts_limit:
        raise ValidationError("Исчерпан лимит попыток для этой работы.")

    submission = Submission(
        publication=publication,
        assignment=publication.assignment,
        variant=variant,
        student=student,
        status=Submission.StatusChoices.IN_PROGRESS,
        attempt_number=next_attempt_number,
        started_at=timezone.now(),
    )
    submission.full_clean()
    submission.save()

    attempt = SubmissionAttempt(
        submission=submission,
        attempt_number=submission.attempt_number,
        status=SubmissionAttempt.StatusChoices.IN_PROGRESS,
        started_at=submission.started_at,
    )
    attempt.full_clean()
    attempt.save()

    logger.info("start_submission completed submission_id=%s", submission.id)
    return submission


@transaction.atomic
def submit_submission(submission: Submission) -> Submission:
    """Отправляет сдачу студента на проверку."""

    logger.info("submit_submission started submission_id=%s", submission.id)

    if submission.status not in {
        Submission.StatusChoices.DRAFT,
        Submission.StatusChoices.IN_PROGRESS,
        Submission.StatusChoices.RETURNED_FOR_REVISION,
    }:
        raise ValidationError("Эту сдачу нельзя отправить повторно.")

    submission.status = Submission.StatusChoices.SUBMITTED
    submission.submitted_at = timezone.now()
    submission.full_clean()
    submission.save()

    attempt = submission.attempts.order_by("-attempt_number", "-id").first()
    if attempt:
        attempt.status = SubmissionAttempt.StatusChoices.SUBMITTED
        attempt.submitted_at = submission.submitted_at

        if submission.started_at and submission.submitted_at:
            attempt.time_spent_minutes = max(
                int((submission.submitted_at - submission.started_at).total_seconds() // 60),
                0,
            )

        attempt.full_clean()
        attempt.save()

    if submission.started_at and submission.submitted_at:
        submission.time_spent_minutes = max(
            int((submission.submitted_at - submission.started_at).total_seconds() // 60),
            0,
        )
        submission.save(update_fields=("time_spent_minutes", "updated_at"))

    logger.info("submit_submission completed submission_id=%s", submission.id)
    return submission
