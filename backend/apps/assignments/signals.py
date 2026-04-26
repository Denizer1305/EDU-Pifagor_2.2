from __future__ import annotations

import logging

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from apps.assignments.models import (
    Assignment,
    AssignmentPolicy,
    AssignmentQuestion,
    AssignmentVariant,
    Submission,
    SubmissionAnswer,
    SubmissionReview,
)
from apps.assignments.services.assignment_structure_services import (
    recalculate_assignment_policy_max_score,
    recalculate_assignment_variant_max_score,
)
from apps.assignments.services.grading_services import (
    calculate_submission_scores,
    sync_submission_review_result,
)

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Assignment)
def ensure_assignment_policy_exists(sender, instance: Assignment, created: bool, **kwargs):
    if created:
        AssignmentPolicy.objects.get_or_create(
            assignment=instance,
            defaults={
                "check_mode": AssignmentPolicy.CheckModeChoices.MANUAL,
                "grading_mode": AssignmentPolicy.GradingModeChoices.RAW_SCORE,
                "max_score": 0,
                "passing_score": 0,
                "attempts_limit": 1,
                "allow_text_answer": True,
            },
        )


@receiver(post_save, sender=AssignmentQuestion)
def question_saved_recalculate_scores(sender, instance: AssignmentQuestion, **kwargs):
    try:
        if instance.variant_id:
            recalculate_assignment_variant_max_score(instance.variant)
        recalculate_assignment_policy_max_score(instance.assignment)
    except Exception:
        logger.exception(
            "Failed to recalculate assignment scores after question save. question_id=%s",
            instance.id,
        )


@receiver(post_delete, sender=AssignmentQuestion)
def question_deleted_recalculate_scores(sender, instance: AssignmentQuestion, **kwargs):
    try:
        if instance.variant_id:
            recalculate_assignment_variant_max_score(instance.variant)
        recalculate_assignment_policy_max_score(instance.assignment)
    except Exception:
        logger.exception(
            "Failed to recalculate assignment scores after question delete. question_id=%s",
            instance.id,
        )


@receiver(post_save, sender=AssignmentVariant)
def variant_saved_recalculate_policy(sender, instance: AssignmentVariant, **kwargs):
    try:
        recalculate_assignment_policy_max_score(instance.assignment)
    except Exception:
        logger.exception(
            "Failed to recalculate policy after variant save. variant_id=%s",
            instance.id,
        )


@receiver(post_delete, sender=AssignmentVariant)
def variant_deleted_recalculate_policy(sender, instance: AssignmentVariant, **kwargs):
    try:
        recalculate_assignment_policy_max_score(instance.assignment)
    except Exception:
        logger.exception(
            "Failed to recalculate policy after variant delete. variant_id=%s",
            instance.id,
        )


@receiver(post_save, sender=SubmissionAnswer)
def submission_answer_saved_update_submission_score(sender, instance: SubmissionAnswer, **kwargs):
    try:
        calculate_submission_scores(instance.submission)
    except Exception:
        logger.exception(
            "Failed to calculate submission scores after answer save. submission_answer_id=%s",
            instance.id,
        )


@receiver(post_delete, sender=SubmissionAnswer)
def submission_answer_deleted_update_submission_score(sender, instance: SubmissionAnswer, **kwargs):
    try:
        calculate_submission_scores(instance.submission)
    except Exception:
        logger.exception(
            "Failed to calculate submission scores after answer delete. submission_answer_id=%s",
            instance.id,
        )


@receiver(post_save, sender=SubmissionReview)
def submission_review_saved_sync_submission(sender, instance: SubmissionReview, **kwargs):
    try:
        sync_submission_review_result(instance)
    except Exception:
        logger.exception(
            "Failed to sync submission review result. review_id=%s",
            instance.id,
        )


@receiver(post_save, sender=Submission)
def submission_saved_fill_started_at(sender, instance: Submission, created: bool, **kwargs):
    if created and instance.status == Submission.StatusChoices.IN_PROGRESS and instance.started_at is None:
        instance.started_at = instance.created_at
        instance.save(update_fields=("started_at", "updated_at"))
