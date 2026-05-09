from __future__ import annotations

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import NotFound

from apps.course.selectors import (
    get_course_by_id,
    get_course_lesson_by_id,
    get_course_module_by_id,
)


def validation_error_payload(exc: DjangoValidationError) -> dict:
    """Преобразует Django ValidationError в payload для DRF ValidationError."""

    if hasattr(exc, "message_dict"):
        return exc.message_dict

    return {"detail": exc.messages}


def get_course_or_404(*, course_pk: int):
    """Возвращает курс или выбрасывает NotFound."""

    course = get_course_by_id(course_id=course_pk)
    if course is None:
        raise NotFound("Курс не найден.")

    return course


def get_module_or_404(*, module_pk: int):
    """Возвращает модуль курса или выбрасывает NotFound."""

    module = get_course_module_by_id(module_id=module_pk)
    if module is None:
        raise NotFound("Модуль не найден.")

    return module


def get_lesson_or_404(*, lesson_pk: int):
    """Возвращает урок курса или выбрасывает NotFound."""

    lesson = get_course_lesson_by_id(lesson_id=lesson_pk)
    if lesson is None:
        raise NotFound("Урок не найден.")

    return lesson
