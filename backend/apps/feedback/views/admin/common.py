from __future__ import annotations

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError

from apps.feedback.filters import FeedbackRequestFilter


def apply_feedback_filter(request, queryset):
    """Применяет фильтр обращений для admin API."""

    filterset = FeedbackRequestFilter(
        data=request.query_params,
        queryset=queryset,
    )

    if not filterset.is_valid():
        raise ValidationError(filterset.errors)

    return filterset.qs


def django_validation_error_payload(exc: DjangoValidationError) -> dict:
    """Преобразует Django ValidationError в payload ответа."""

    if hasattr(exc, "message_dict"):
        return exc.message_dict

    return {"detail": exc.messages}
