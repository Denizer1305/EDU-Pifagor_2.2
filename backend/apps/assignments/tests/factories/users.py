from __future__ import annotations

from apps.assignments.tests.factories.common import extract_user, unique_email
from apps.users.tests.factories import (
    create_admin_user as base_create_admin_user,
    create_student_user as base_create_student_user,
    create_teacher_user as base_create_teacher_user,
)


def create_teacher_user(email: str | None = None):
    """Создаёт тестового преподавателя."""

    created = base_create_teacher_user(
        email=email or unique_email("assignments_teacher"),
    )
    return extract_user(created)


def create_student_user(email: str | None = None):
    """Создаёт тестового студента."""

    created = base_create_student_user(
        email=email or unique_email("assignments_student"),
    )
    return extract_user(created)


def create_admin_user(email: str | None = None):
    """Создаёт тестового администратора."""

    created = base_create_admin_user(
        email=email or unique_email("assignments_admin"),
    )
    return extract_user(created)
