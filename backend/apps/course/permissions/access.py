from __future__ import annotations

from apps.course.models import Course
from apps.course.permissions.roles import is_admin_user


def _is_active_course_teacher(user, course: Course) -> bool:
    """Проверяет, является ли пользователь активным преподавателем курса."""

    if not user or not user.is_authenticated or course is None:
        return False

    if is_admin_user(user):
        return True

    return course.course_teachers.filter(
        teacher=user,
        is_active=True,
    ).exists()


def _is_course_owner(user, course: Course) -> bool:
    """Проверяет, является ли пользователь владельцем курса."""

    if not user or not user.is_authenticated or course is None:
        return False

    if is_admin_user(user):
        return True

    return course.course_teachers.filter(
        teacher=user,
        is_active=True,
        role="owner",
    ).exists()
