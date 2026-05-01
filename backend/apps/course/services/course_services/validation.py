from __future__ import annotations

from django.core.exceptions import ValidationError

from apps.course.models import Course


def _validate_course_can_be_published(course: Course) -> None:
    """Проверяет, можно ли опубликовать курс."""

    if not course.title:
        raise ValidationError(
            {"title": "Нельзя публиковать курс без названия."}
        )

    if not course.modules.exists():
        raise ValidationError(
            {"status": "Нельзя публиковать курс без модулей."}
        )

    has_published_lessons = course.lessons.filter(
        is_published=True,
        module__is_published=True,
    ).exists()

    if not has_published_lessons:
        raise ValidationError(
            {"status": "Нельзя публиковать курс без опубликованных уроков."}
        )
