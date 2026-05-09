from __future__ import annotations

from apps.feedback.models import FeedbackRequest


def _reload_feedback_request(feedback_request: FeedbackRequest) -> FeedbackRequest:
    """Возвращает обращение с основными связанными объектами после изменений."""

    return FeedbackRequest.objects.select_related(
        "processing",
        "contact",
        "technical",
    ).get(pk=feedback_request.pk)
