from __future__ import annotations

from django.contrib.auth import get_user_model

from apps.organizations.tests.factories.counters import (
    non_teacher_counter,
    teacher_counter,
)
from apps.users.constants import ROLE_TEACHER
from apps.users.services.profile_services import (
    ensure_role_profile,
    get_or_create_base_profile,
)
from apps.users.tests.factories import assign_role

User = get_user_model()


def _build_user(
    *,
    email: str,
    password: str,
    registration_type: str,
    first_name: str,
    last_name: str,
    patronymic: str,
):
    """Создаёт пользователя с базовым профилем и роль-профилем."""

    user = User.objects.create_user(
        email=email,
        password=password,
        registration_type=registration_type,
    )

    profile = get_or_create_base_profile(user)
    profile.first_name = first_name
    profile.last_name = last_name
    profile.patronymic = patronymic
    profile.full_clean()
    profile.save()

    ensure_role_profile(user)
    return user


def create_teacher_user(
    *,
    email: str | None = None,
    password: str = "TestPass123!",
):
    """Создаёт тестового преподавателя."""

    index = next(teacher_counter)

    if email is None:
        email = f"teacher_org_{index}@example.com"

    user = _build_user(
        email=email,
        password=password,
        registration_type="teacher",
        first_name="Мария",
        last_name=f"Петрова{index}",
        patronymic="Игоревна",
    )
    assign_role(user=user, code=ROLE_TEACHER)
    return user


def create_non_teacher_user(
    *,
    email: str | None = None,
    password: str = "TestPass123!",
    registration_type: str = "student",
):
    """Создаёт тестового пользователя без роли преподавателя."""

    index = next(non_teacher_counter)

    if email is None:
        email = f"simple_org_{index}@example.com"

    return _build_user(
        email=email,
        password=password,
        registration_type=registration_type,
        first_name="Иван",
        last_name=f"Сидоров{index}",
        patronymic="Петрович",
    )
