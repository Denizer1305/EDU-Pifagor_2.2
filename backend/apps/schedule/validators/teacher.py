from __future__ import annotations

from typing import Any

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_teacher_registration_type(
    teacher: Any,
    *,
    field_name: str = "teacher",
) -> None:
    if teacher is None:
        return

    registration_type = getattr(teacher, "registration_type", "")

    if registration_type and registration_type != "teacher":
        raise ValidationError(
            {
                field_name: _(
                    "Преподавателем может быть только пользователь "
                    "с типом регистрации teacher."
                )
            }
        )


def validate_teacher_is_active_for_schedule(
    teacher: Any,
    *,
    field_name: str = "teacher",
) -> None:
    if teacher is None:
        return

    validate_teacher_registration_type(teacher, field_name=field_name)

    if getattr(teacher, "is_active", True) is False:
        raise ValidationError(
            {field_name: _("Нельзя назначить неактивного преподавателя.")}
        )

    if getattr(teacher, "is_email_verified", None) is False:
        raise ValidationError(
            {
                field_name: _(
                    "Нельзя назначить преподавателя "
                    "с неподтвержденной электронной почтой."
                )
            }
        )

    onboarding_status = getattr(teacher, "onboarding_status", "")
    if onboarding_status and onboarding_status != "active":
        raise ValidationError(
            {
                field_name: _(
                    "Нельзя назначить преподавателя с незавершенным онбордингом."
                )
            }
        )
