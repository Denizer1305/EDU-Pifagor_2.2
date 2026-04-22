from __future__ import annotations

import logging

from django.db import transaction
from django.utils import timezone

from apps.feedback.models import (
    FeedbackRequest,
    FeedbackRequestProcessing,
    FeedbackStatusHistory,
)
from apps.feedback.models.base import normalize_text

logger = logging.getLogger(__name__)


def _get_or_create_processing(
    feedback_request: FeedbackRequest,
) -> FeedbackRequestProcessing:
    processing, _ = FeedbackRequestProcessing.objects.get_or_create(
        feedback_request=feedback_request,
    )
    return processing


def _create_status_history(
    *,
    feedback_request: FeedbackRequest,
    from_status: str,
    to_status: str,
    changed_by=None,
    comment: str = "",
) -> FeedbackStatusHistory:
    history = FeedbackStatusHistory(
        feedback_request=feedback_request,
        from_status=normalize_text(from_status),
        to_status=to_status,
        changed_by=changed_by,
        comment=normalize_text(comment),
    )
    history.full_clean()
    history.save()
    return history


def _set_feedback_status(
    *,
    feedback_request: FeedbackRequest,
    new_status: str,
    changed_by=None,
    comment: str = "",
) -> FeedbackRequest:
    old_status = feedback_request.status
    feedback_request.status = new_status
    feedback_request.full_clean()
    feedback_request.save(update_fields=["status", "updated_at"])

    _create_status_history(
        feedback_request=feedback_request,
        from_status=old_status,
        to_status=new_status,
        changed_by=changed_by,
        comment=comment,
    )
    return feedback_request


def _mark_processing_completed(
    *,
    processing: FeedbackRequestProcessing,
    admin_user,
    reply_message: str = "",
    internal_note: str = "",
    is_spam_suspected: bool | None = None,
) -> FeedbackRequestProcessing:
    processing.processed_by = admin_user
    processing.processed_at = timezone.now()
    processing.reply_message = normalize_text(reply_message)

    if internal_note:
        processing.internal_note = normalize_text(internal_note)

    if is_spam_suspected is not None:
        processing.is_spam_suspected = is_spam_suspected

    processing.full_clean()
    processing.save()
    return processing


def _reload_feedback_request(feedback_request: FeedbackRequest) -> FeedbackRequest:
    return FeedbackRequest.objects.select_related(
        "processing",
        "contact",
        "technical",
    ).get(pk=feedback_request.pk)


@transaction.atomic
def mark_feedback_in_progress(
    *,
    feedback_request: FeedbackRequest,
    admin_user,
    internal_note: str = "",
) -> FeedbackRequest:
    logger.info(
        "mark_feedback_in_progress started feedback_request_id=%s admin_user_id=%s",
        feedback_request.id,
        getattr(admin_user, "id", None),
    )

    processing = _get_or_create_processing(feedback_request)
    processing.assigned_to = admin_user

    if processing.assigned_at is None:
        processing.assigned_at = timezone.now()

    if internal_note:
        processing.internal_note = normalize_text(internal_note)

    processing.processed_by = None
    processing.processed_at = None
    processing.full_clean()
    processing.save()

    feedback_request = _set_feedback_status(
        feedback_request=feedback_request,
        new_status=FeedbackRequest.StatusChoices.IN_PROGRESS,
        changed_by=admin_user,
        comment=internal_note or "Обращение взято в работу.",
    )

    logger.info(
        "mark_feedback_in_progress completed feedback_request_id=%s",
        feedback_request.id,
    )
    return _reload_feedback_request(feedback_request)


@transaction.atomic
def resolve_feedback_request(
    *,
    feedback_request: FeedbackRequest,
    admin_user,
    reply_message: str = "",
    internal_note: str = "",
) -> FeedbackRequest:
    logger.info(
        "resolve_feedback_request started feedback_request_id=%s admin_user_id=%s",
        feedback_request.id,
        getattr(admin_user, "id", None),
    )

    processing = _get_or_create_processing(feedback_request)
    _mark_processing_completed(
        processing=processing,
        admin_user=admin_user,
        reply_message=reply_message,
        internal_note=internal_note,
    )

    feedback_request = _set_feedback_status(
        feedback_request=feedback_request,
        new_status=FeedbackRequest.StatusChoices.RESOLVED,
        changed_by=admin_user,
        comment=internal_note or "Обращение решено.",
    )

    logger.info(
        "resolve_feedback_request completed feedback_request_id=%s",
        feedback_request.id,
    )
    return _reload_feedback_request(feedback_request)


@transaction.atomic
def reject_feedback_request(
    *,
    feedback_request: FeedbackRequest,
    admin_user,
    reply_message: str = "",
    internal_note: str = "",
) -> FeedbackRequest:
    logger.info(
        "reject_feedback_request started feedback_request_id=%s admin_user_id=%s",
        feedback_request.id,
        getattr(admin_user, "id", None),
    )

    processing = _get_or_create_processing(feedback_request)
    _mark_processing_completed(
        processing=processing,
        admin_user=admin_user,
        reply_message=reply_message,
        internal_note=internal_note,
    )

    feedback_request = _set_feedback_status(
        feedback_request=feedback_request,
        new_status=FeedbackRequest.StatusChoices.REJECTED,
        changed_by=admin_user,
        comment=internal_note or "Обращение отклонено.",
    )

    logger.info(
        "reject_feedback_request completed feedback_request_id=%s",
        feedback_request.id,
    )
    return _reload_feedback_request(feedback_request)


@transaction.atomic
def mark_feedback_as_spam(
    *,
    feedback_request: FeedbackRequest,
    admin_user,
    internal_note: str = "",
) -> FeedbackRequest:
    logger.info(
        "mark_feedback_as_spam started feedback_request_id=%s admin_user_id=%s",
        feedback_request.id,
        getattr(admin_user, "id", None),
    )

    processing = _get_or_create_processing(feedback_request)
    _mark_processing_completed(
        processing=processing,
        admin_user=admin_user,
        internal_note=internal_note,
        is_spam_suspected=True,
    )

    feedback_request = _set_feedback_status(
        feedback_request=feedback_request,
        new_status=FeedbackRequest.StatusChoices.SPAM,
        changed_by=admin_user,
        comment=internal_note or "Обращение помечено как спам.",
    )

    logger.info(
        "mark_feedback_as_spam completed feedback_request_id=%s",
        feedback_request.id,
    )
    return _reload_feedback_request(feedback_request)


@transaction.atomic
def archive_feedback_request(
    *,
    feedback_request: FeedbackRequest,
    admin_user,
    internal_note: str = "",
) -> FeedbackRequest:
    logger.info(
        "archive_feedback_request started feedback_request_id=%s admin_user_id=%s",
        feedback_request.id,
        getattr(admin_user, "id", None),
    )

    processing = _get_or_create_processing(feedback_request)

    if processing.processed_at is None:
        processing.processed_at = timezone.now()

    if processing.processed_by is None:
        processing.processed_by = admin_user

    if internal_note:
        processing.internal_note = normalize_text(internal_note)

    processing.full_clean()
    processing.save()

    feedback_request = _set_feedback_status(
        feedback_request=feedback_request,
        new_status=FeedbackRequest.StatusChoices.ARCHIVED,
        changed_by=admin_user,
        comment=internal_note or "Обращение отправлено в архив.",
    )

    logger.info(
        "archive_feedback_request completed feedback_request_id=%s",
        feedback_request.id,
    )
    return _reload_feedback_request(feedback_request)
