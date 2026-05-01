from __future__ import annotations

from django.utils import timezone

from apps.users.constants import (
    VERIFICATION_STATUS_NOT_FILLED,
    VERIFICATION_STATUS_PENDING,
)


def _configure_student_profile(role_profile) -> None:
    """Настраивает профиль студента после регистрации."""

    role_profile.verification_status = VERIFICATION_STATUS_NOT_FILLED
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

    if hasattr(role_profile, "requested_organization"):
        role_profile.requested_organization = requested_organization

    if hasattr(role_profile, "requested_department"):
        role_profile.requested_department = requested_department

    if hasattr(role_profile, "position"):
        role_profile.position = position

    if hasattr(role_profile, "employee_code"):
        role_profile.employee_code = employee_code

    if hasattr(role_profile, "education_info"):
        role_profile.education_info = education_info

    if hasattr(role_profile, "experience_years") and experience_years is not None:
        role_profile.experience_years = experience_years

    if hasattr(role_profile, "verification_status"):
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

    if hasattr(role_profile, "position"):
        role_profile.position = position

    if hasattr(role_profile, "work_place"):
        role_profile.work_place = work_place

    role_profile.full_clean()
    role_profile.save()
