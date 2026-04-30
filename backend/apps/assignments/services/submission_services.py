from __future__ import annotations

import logging
from decimal import Decimal

from django.apps import apps
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Max
from django.utils import timezone

from apps.assignments.models import (
    AssignmentAudience,
    AssignmentPolicy,
    Submission,
    SubmissionAnswer,
    SubmissionAttachment,
    SubmissionAttempt,
)

logger = logging.getLogger(__name__)


def _get_assignment_policy(assignment) -> AssignmentPolicy:
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


def _student_in_group_audience(publication, student) -> bool:
    group_ids = list(
        publication.audiences.filter(
            audience_type=AssignmentAudience.AudienceTypeChoices.GROUP,
            is_active=True,
            group__isnull=False,
        ).values_list("group_id", flat=True)
    )
    if not group_ids:
        return False

    StudentGroupEnrollment = apps.get_model("education", "StudentGroupEnrollment")
    return StudentGroupEnrollment.objects.filter(
        student=student,
        group_id__in=group_ids,
    ).exists()


def _student_in_course(publication, student) -> bool:
    if publication.course_id is None:
        return False

    CourseEnrollment = apps.get_model("course", "CourseEnrollment")
    return CourseEnrollment.objects.filter(
        course=publication.course,
        student=student,
    ).exists()


def _is_student_assigned(publication, student) -> bool:
    audiences = publication.audiences.filter(is_active=True)

    if not audiences.exists():
        return False

    if audiences.filter(
        audience_type=AssignmentAudience.AudienceTypeChoices.ALL_COURSE_STUDENTS,
    ).exists():
        return _student_in_course(publication, student)

    if audiences.filter(
        audience_type__in=(
            AssignmentAudience.AudienceTypeChoices.STUDENT,
            AssignmentAudience.AudienceTypeChoices.SELECTED_STUDENTS,
        ),
        student=student,
    ).exists():
        return True

    if audiences.filter(
        course_enrollment__student=student,
    ).exists():
        return True

    return _student_in_group_audience(publication, student)


def _get_next_attempt_number(publication, student) -> int:
    max_attempt = Submission.objects.filter(
        publication=publication,
        student=student,
    ).aggregate(value=Max("attempt_number"))["value"]
    return (max_attempt or 0) + 1


@transaction.atomic
def start_submission(
    *,
    publication,
    student,
    variant=None,
) -> Submission:
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

    if not _is_student_assigned(publication, student):
        raise ValidationError("Эта работа не назначена данному студенту.")

    policy = _get_assignment_policy(publication.assignment)

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

    next_attempt_number = _get_next_attempt_number(publication, student)
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
def save_submission_answer(
    *,
    submission: Submission,
    question,
    answer_text: str = "",
    answer_json: dict | None = None,
    selected_options_json: list | None = None,
    numeric_answer=None,
) -> SubmissionAnswer:
    if submission.status not in {
        Submission.StatusChoices.DRAFT,
        Submission.StatusChoices.IN_PROGRESS,
        Submission.StatusChoices.RETURNED_FOR_REVISION,
    }:
        raise ValidationError("Нельзя редактировать ответы после отправки работы.")

    answer, _ = SubmissionAnswer.objects.get_or_create(
        submission=submission,
        question=question,
    )
    answer.answer_text = answer_text
    answer.answer_json = answer_json or {}
    answer.selected_options_json = selected_options_json or []
    answer.numeric_answer = numeric_answer
    answer.full_clean()
    answer.save()
    return answer


@transaction.atomic
def attach_file_to_submission(
    *,
    submission: Submission,
    file,
    question=None,
    attachment_type: str = SubmissionAttachment.AttachmentTypeChoices.OTHER,
) -> SubmissionAttachment:
    if submission.status not in {
        Submission.StatusChoices.DRAFT,
        Submission.StatusChoices.IN_PROGRESS,
        Submission.StatusChoices.RETURNED_FOR_REVISION,
    }:
        raise ValidationError("Нельзя прикреплять файлы после отправки работы.")

    attachment = SubmissionAttachment(
        submission=submission,
        question=question,
        file=file,
        attachment_type=attachment_type,
    )
    attachment.full_clean()
    attachment.save()
    return attachment


@transaction.atomic
def submit_submission(submission: Submission) -> Submission:
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


@transaction.atomic
def create_new_submission_attempt(submission: Submission) -> Submission:
    logger.info("create_new_submission_attempt started submission_id=%s", submission.id)

    policy = _get_assignment_policy(submission.assignment)
    next_attempt_number = _get_next_attempt_number(
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
