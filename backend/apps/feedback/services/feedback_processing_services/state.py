from __future__ import annotations

from django.utils import timezone

from apps.feedback.models import (
    FeedbackRequest,
    FeedbackRequestProcessing,
)
from apps.feedback.models.base import normalize_text
from apps.feedback.services.feedback_processing_services.history import (
    _create_status_history,
)


def _set_feedback_status(
    *,
    feedback_request: FeedbackRequest,
    new_status: str,
    changed_by=None,
    comment: str = "",
) -> FeedbackRequest:
    """Меняет статус обращения и создаёт запись истории."""

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
    """Заполняет данные обработки обращения."""

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
