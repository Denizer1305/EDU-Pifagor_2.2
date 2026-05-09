from __future__ import annotations

import logging

from django.db import transaction
from django.utils import timezone

from apps.feedback.models import FeedbackRequest
from apps.feedback.models.base import normalize_text
from apps.feedback.services.feedback_processing_services.common import (
    _reload_feedback_request,
)
from apps.feedback.services.feedback_processing_services.history import (
    _get_or_create_processing,
)
from apps.feedback.services.feedback_processing_services.state import (
    _mark_processing_completed,
    _set_feedback_status,
)

logger = logging.getLogger(__name__)


@transaction.atomic
def mark_feedback_in_progress(
    *,
    feedback_request: FeedbackRequest,
    admin_user,
    internal_note: str = "",
) -> FeedbackRequest:
    """Переводит обращение в работу и назначает ответственного администратора."""

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
    """Помечает обращение как решённое."""

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
    """Отклоняет обращение."""

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
    """Помечает обращение как спам."""

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
    """Архивирует обращение."""

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
