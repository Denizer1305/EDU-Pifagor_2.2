from __future__ import annotations

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import NotFound, ValidationError

from apps.course.selectors import get_course_by_id


def apply_filterset(filterset_class, request, queryset):
    """Применяет django-filter FilterSet к queryset."""

    filterset = filterset_class(
        data=request.query_params,
        queryset=queryset,
    )

    if not filterset.is_valid():
        raise ValidationError(filterset.errors)

    return filterset.qs


def validation_error_payload(exc: DjangoValidationError) -> dict:
    """Преобразует Django ValidationError в payload для DRF ValidationError."""

    if hasattr(exc, "message_dict"):
        return exc.message_dict

    return {"detail": exc.messages}


def get_course_or_404(*, course_id: int):
    """Возвращает курс или выбрасывает NotFound."""

    course = get_course_by_id(course_id=course_id)
    if course is None:
        raise NotFound("Курс не найден.")

    return course
