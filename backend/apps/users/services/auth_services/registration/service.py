from __future__ import annotations

from django.db import transaction

from apps.users.constants import (
    REGISTRATION_TYPE_STUDENT,
    REGISTRATION_TYPE_TEACHER,
)
from apps.users.services.auth_services.registration.normalizers import (
    _normalize_registration_data,
)
from apps.users.services.auth_services.registration.profile_setup import (
    _configure_other_role_profile,
    _configure_student_profile,
    _configure_teacher_profile,
)
from apps.users.services.auth_services.registration.user_factory import (
    _create_user_with_profile,
)
from apps.users.services.auth_services.registration.validators import (
    _validate_registration_base,
    _validate_teacher_registration,
)
from apps.users.services.profile_services import ensure_role_profile


@transaction.atomic
def register_user(
    *,
    email: str,
    password: str,
    password_repeat: str,
    registration_type: str,
    first_name: str,
    last_name: str,
    patronymic: str = "",
    phone: str = "",
    reset_email: str = "",
    requested_organization=None,
    requested_department=None,
    teacher_registration_code: str = "",
    position: str = "",
    employee_code: str = "",
    work_place: str = "",
    education_info: str = "",
    experience_years: int | None = None,
):
    """Регистрирует пользователя и подготавливает профиль под нужный flow."""

    normalized = _normalize_registration_data(
        email=email,
        reset_email=reset_email,
        first_name=first_name,
        last_name=last_name,
        patronymic=patronymic,
        phone=phone,
        position=position,
        employee_code=employee_code,
        work_place=work_place,
        education_info=education_info,
    )

    _validate_registration_base(
        email=normalized["email"],
        reset_email=normalized["reset_email"],
        phone=normalized["phone"],
        password=password,
        password_repeat=password_repeat,
    )

    if registration_type == REGISTRATION_TYPE_TEACHER:
        _validate_teacher_registration(
            requested_organization=requested_organization,
            requested_department=requested_department,
            teacher_registration_code=teacher_registration_code,
        )

    user = _create_user_with_profile(
        email=normalized["email"],
        password=password,
        reset_email=normalized["reset_email"],
        registration_type=registration_type,
        first_name=normalized["first_name"],
        last_name=normalized["last_name"],
        patronymic=normalized["patronymic"],
        phone=normalized["phone"],
    )

    role_profile = ensure_role_profile(user)

    if registration_type == REGISTRATION_TYPE_STUDENT and role_profile:
        _configure_student_profile(role_profile)

    if registration_type == REGISTRATION_TYPE_TEACHER and role_profile:
        _configure_teacher_profile(
            role_profile=role_profile,
            requested_organization=requested_organization,
            requested_department=requested_department,
            position=normalized["position"],
            employee_code=normalized["employee_code"],
            education_info=normalized["education_info"],
            experience_years=experience_years,
        )

    if (
        registration_type not in {REGISTRATION_TYPE_STUDENT, REGISTRATION_TYPE_TEACHER}
        and role_profile
    ):
        _configure_other_role_profile(
            role_profile=role_profile,
            position=normalized["position"],
            work_place=normalized["work_place"],
        )

    return user
