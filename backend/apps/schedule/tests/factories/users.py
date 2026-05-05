from __future__ import annotations

from typing import Any

from apps.schedule.tests.factories.context import next_number
from apps.users.models import User


def create_user(
    *,
    email: str | None = None,
    password: str = "TestPass123!",
    registration_type: str = "teacher",
    is_staff: bool = False,
    is_superuser: bool = False,
    **extra_fields: Any,
) -> User:
    number = next_number()
    email = email or f"schedule-user-{number}@example.com"

    user = User.objects.create_user(
        email=email,
        password=password,
        registration_type=registration_type,
        **extra_fields,
    )
    user.is_staff = is_staff
    user.is_superuser = is_superuser
    user.save(update_fields=("is_staff", "is_superuser"))

    return user


def create_teacher(
    *,
    email: str | None = None,
    **extra_fields: Any,
) -> User:
    return create_user(
        email=email,
        registration_type="teacher",
        **extra_fields,
    )


def create_student(
    *,
    email: str | None = None,
    **extra_fields: Any,
) -> User:
    return create_user(
        email=email,
        registration_type="student",
        **extra_fields,
    )


def create_admin(
    *,
    email: str | None = None,
    **extra_fields: Any,
) -> User:
    return create_user(
        email=email,
        registration_type="admin",
        is_staff=True,
        is_superuser=True,
        **extra_fields,
    )
