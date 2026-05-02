from __future__ import annotations

from uuid import uuid4

from apps.course.tests.factories.common import _unwrap_factory_result
from apps.users.tests.factories import (
    create_admin_user as base_create_admin_user,
)
from apps.users.tests.factories import (
    create_student_user as base_create_student_user,
)
from apps.users.tests.factories import (
    create_teacher_user as base_create_teacher_user,
)


def create_course_author(*, email: str | None = None):
    """Создаёт тестового автора курса."""

    if email is None:
        email = f"course_teacher_{uuid4().hex[:8]}@example.com"

    return _unwrap_factory_result(base_create_teacher_user(email=email))


def create_course_student(*, email: str | None = None):
    """Создаёт тестового студента курса."""

    if email is None:
        email = f"course_student_{uuid4().hex[:8]}@example.com"

    return _unwrap_factory_result(base_create_student_user(email=email))


def create_course_admin(*, email: str | None = None):
    """Создаёт тестового администратора."""

    if email is None:
        email = f"course_admin_{uuid4().hex[:8]}@example.com"

    return _unwrap_factory_result(base_create_admin_user(email=email))
