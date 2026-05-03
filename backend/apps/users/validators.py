from __future__ import annotations

import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from apps.users.constants import ONBOARDING_STATUS_ACTIVE

PHONE_RE = re.compile(r"^\+?[0-9()\-\s]{7,20}$")


def _has_field(model, field_name: str) -> bool:
    return field_name in {field.name for field in model._meta.get_fields()}


def _get_email_verified_value(user) -> bool:
    if hasattr(user, "is_email_verified"):
        return bool(user.is_email_verified)
    return False


def validate_email(email: str, reset_email: str = "") -> None:
    email = (email or "").strip().lower()
    reset_email = (reset_email or "").strip().lower()

    if not email:
        raise ValidationError({"email": _("Введите эл. почту.")})

    if reset_email and email == reset_email:
        raise ValidationError(
            {"reset_email": _("Резервная почта не должна совпадать с основной.")}
        )


def validate_phone(phone: str) -> None:
    phone = (phone or "").strip()
    if phone and not PHONE_RE.match(phone):
        raise ValidationError({"phone": _("Некорректный формат телефона.")})


def validate_user_onboarding_transition(user) -> None:
    if (
        user.onboarding_status == ONBOARDING_STATUS_ACTIVE
        and not _get_email_verified_value(user)
    ):
        raise ValidationError(
            {
                "onboarding_status": _(
                    "Нельзя активировать пользователя без подтвержденной почты."
                )
            }
        )


def validate_student_profile_request(student_profile) -> None:
    requested_organization = getattr(student_profile, "requested_organization", None)
    requested_department = getattr(student_profile, "requested_department", None)
    requested_group = getattr(student_profile, "requested_group", None)

    if (
        requested_department
        and requested_organization
        and requested_department.organization_id != requested_organization.id
    ):
        raise ValidationError(
            {
                "requested_department": _(
                    "Отделение должно принадлежать выбранной образовательной организации."
                )
            }
        )

    if (
        requested_group
        and requested_organization
        and requested_group.organization_id != requested_organization.id
    ):
        raise ValidationError(
            {
                "requested_group": _(
                    "Группа должна принадлежать выбранной образовательной организации."
                )
            }
        )

    if (
        requested_group
        and requested_department
        and requested_group.department_id
        and requested_group.department_id != requested_department.id
    ):
        raise ValidationError(
            {"requested_group": _("Группа должна принадлежать выбранному отделению.")}
        )


def validate_teacher_profile_request(teacher_profile) -> None:
    requested_organization = getattr(teacher_profile, "requested_organization", None)
    requested_department = getattr(teacher_profile, "requested_department", None)

    if (
        requested_department
        and requested_organization
        and requested_department.organization_id != requested_organization.id
    ):
        raise ValidationError(
            {
                "requested_department": _(
                    "Подразделение должно принадлежать выбранной образовательной организации."
                )
            }
        )


def validate_parent_student_link(link) -> None:
    if (
        getattr(link, "parent_id", None)
        and getattr(link, "student_id", None)
        and link.parent_id == link.student_id
    ):
        raise ValidationError(
            {"student": _("Нельзя создать связь пользователя с самим собой.")}
        )
