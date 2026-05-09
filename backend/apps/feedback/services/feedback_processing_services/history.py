from __future__ import annotations

from apps.feedback.models import (
    FeedbackRequest,
    FeedbackRequestProcessing,
    FeedbackStatusHistory,
)
from apps.feedback.models.base import normalize_text


def _get_or_create_processing(
    feedback_request: FeedbackRequest,
) -> FeedbackRequestProcessing:
    """Возвращает processing-запись обращения или создаёт её."""

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
    """Создаёт запись истории изменения статуса обращения."""

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
