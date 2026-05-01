from __future__ import annotations

from django.contrib.auth import get_user_model, password_validation
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from apps.users.services.auth_services.teacher_code import (
    _verify_teacher_registration_code,
)
from apps.users.validators import validate_email, validate_phone

User = get_user_model()


def _validate_registration_base(
    *,
    email: str,
    reset_email: str,
    phone: str,
    password: str,
    password_repeat: str,
) -> None:
    """Проверяет базовые данные регистрации."""

    if not email:
        raise ValidationError({"email": _("Введите эл. почту.")})

    if User.objects.filter(email=email).exists():
        raise ValidationError(
            {
                "email": _(
                    "Пользователь с такой эл. почтой уже существует."
                )
            }
        )

    validate_email(email, reset_email)

    if phone:
        validate_phone(phone)

    if password != password_repeat:
        raise ValidationError(
            {
                "password_repeat": _("Пароли не совпадают.")
            }
        )

    password_validation.validate_password(password)


def _validate_teacher_registration(
    *,
    requested_organization,
    requested_department,
    teacher_registration_code: str,
) -> None:
    """Проверяет данные регистрации преподавателя."""

    if not requested_organization:
        raise ValidationError(
            {
                "requested_organization": _(
                    "Для преподавателя необходимо указать "
                    "образовательную организацию."
                )
            }
        )

    if (
        requested_department
        and requested_department.organization_id != requested_organization.id
    ):
        raise ValidationError(
            {
                "requested_department": _(
                    "Отделение должно принадлежать выбранной "
                    "образовательной организации."
                )
            }
        )

    _verify_teacher_registration_code(
        organization=requested_organization,
        code=teacher_registration_code,
    )
