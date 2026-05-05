from __future__ import annotations

from typing import Any

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_course_lesson_belongs_to_course(
    course_lesson: Any,
    course_id: int | None,
    *,
    field_name: str = "course_lesson",
) -> None:
    if course_lesson is None or not course_id:
        return

    if getattr(course_lesson, "course_id", None) != course_id:
        raise ValidationError(
            {field_name: _("Занятие курса должно относиться к выбранному курсу.")}
        )


def validate_group_subject_matches_schedule_context(
    group_subject: Any,
    *,
    group_id: int | None = None,
    subject_id: int | None = None,
    academic_year_id: int | None = None,
    education_period_id: int | None = None,
    field_name: str = "group_subject",
) -> None:
    if group_subject is None:
        return

    errors: dict[str, str] = {}

    if group_id and getattr(group_subject, "group_id", None) != group_id:
        errors[field_name] = _("Предмет группы должен относиться к выбранной группе.")

    if subject_id and getattr(group_subject, "subject_id", None) != subject_id:
        errors[field_name] = _(
            "Предмет группы должен относиться к выбранному предмету."
        )

    if (
        academic_year_id
        and getattr(group_subject, "academic_year_id", None) != academic_year_id
    ):
        errors[field_name] = _(
            "Предмет группы должен относиться к выбранному учебному году."
        )

    period_id = getattr(group_subject, "period_id", None)
    if education_period_id and period_id and period_id != education_period_id:
        errors[field_name] = _(
            "Предмет группы должен относиться к выбранному учебному периоду."
        )

    if errors:
        raise ValidationError(errors)
