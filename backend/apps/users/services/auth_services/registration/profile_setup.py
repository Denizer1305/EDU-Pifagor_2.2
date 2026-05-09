from __future__ import annotations

from django.utils import timezone

from apps.users.constants import (
    VERIFICATION_STATUS_NOT_FILLED,
    VERIFICATION_STATUS_PENDING,
)


def _model_has_field(instance, field_name: str) -> bool:
    """Проверяет, есть ли поле у Django-модели."""

    return any(field.name == field_name for field in instance._meta.get_fields())


def _set_field_if_exists(instance, field_name: str, value) -> None:
    """Устанавливает значение поля, если поле существует у модели."""

    if _model_has_field(instance, field_name):
        setattr(instance, field_name, value)


def _configure_student_profile(role_profile) -> None:
    """Настраивает профиль студента после регистрации."""

    _set_field_if_exists(
        role_profile,
        "verification_status",
        VERIFICATION_STATUS_NOT_FILLED,
    )

    role_profile.full_clean()
    role_profile.save()


def _configure_teacher_profile(
    *,
    role_profile,
    requested_organization,
    requested_department,
    position: str,
    employee_code: str,
    education_info: str,
    experience_years: int | None,
) -> None:
    """Настраивает профиль преподавателя после регистрации."""

    role_profile.requested_organization = requested_organization
    role_profile.requested_department = requested_department
    role_profile.position = position
    role_profile.employee_code = employee_code
    role_profile.education_info = education_info

    if experience_years is not None:
        role_profile.experience_years = experience_years

    role_profile.verification_status = VERIFICATION_STATUS_PENDING

    if hasattr(role_profile, "code_verified_at"):
        role_profile.code_verified_at = timezone.now()

    role_profile.full_clean()
    role_profile.save()


def _configure_other_role_profile(
    *,
    role_profile,
    position: str,
    work_place: str,
) -> None:
    """Настраивает профиль родителя или другого типа пользователя."""

    _set_field_if_exists(role_profile, "position", position)
    _set_field_if_exists(role_profile, "work_place", work_place)

    role_profile.full_clean()
    role_profile.save()
