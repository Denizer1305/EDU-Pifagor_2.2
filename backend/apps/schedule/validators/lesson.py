from __future__ import annotations

from typing import Any

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_lesson_not_locked(lesson: Any) -> None:
    if lesson is None:
        return

    if getattr(lesson, "is_locked", False):
        raise ValidationError(
            {"lesson": _("Занятие заблокировано и не может быть изменено.")}
        )


def validate_lesson_can_be_published(lesson: Any) -> None:
    if lesson is None:
        return

    errors: dict[str, str] = {}

    if not getattr(lesson, "date", None):
        errors["date"] = _("Для публикации нужно указать дату занятия.")

    if not getattr(lesson, "starts_at", None):
        errors["starts_at"] = _("Для публикации нужно указать время начала.")

    if not getattr(lesson, "ends_at", None):
        errors["ends_at"] = _("Для публикации нужно указать время окончания.")

    if not getattr(lesson, "teacher_id", None):
        errors["teacher"] = _("Для публикации нужно указать преподавателя.")

    if not getattr(lesson, "group_id", None):
        errors["group"] = _("Для публикации нужно указать группу.")

    if errors:
        raise ValidationError(errors)
