from __future__ import annotations

from typing import Any

from rest_framework.permissions import SAFE_METHODS, BasePermission


def _is_authenticated(user: Any) -> bool:
    return bool(user and user.is_authenticated)


def _is_admin(user: Any) -> bool:
    return bool(
        _is_authenticated(user)
        and (
            user.is_staff or user.is_superuser or _has_role(user, "admin", "methodist")
        )
    )


def _is_teacher(user: Any) -> bool:
    return bool(
        _is_authenticated(user) and (_is_admin(user) or _has_role(user, "teacher"))
    )


def _has_role(user: Any, *role_codes: str) -> bool:
    """Проверяет роли пользователя без жёсткой привязки к related_name."""

    if not _is_authenticated(user):
        return False

    if hasattr(user, "has_role"):
        return bool(user.has_role(*role_codes))

    role_codes_set = set(role_codes)

    user_roles = getattr(user, "user_roles", None)
    if user_roles is not None:
        return user_roles.filter(role__code__in=role_codes_set).exists()

    roles = getattr(user, "roles", None)
    if roles is not None:
        return roles.filter(code__in=role_codes_set).exists()

    return False


def _get_lesson(obj: Any) -> Any | None:
    if hasattr(obj, "lesson"):
        return obj.lesson

    if hasattr(obj, "journal_lesson"):
        return obj.journal_lesson

    if hasattr(obj, "date") and hasattr(obj, "course_id") and hasattr(obj, "group_id"):
        return obj

    return None


def _is_lesson_teacher(user: Any, obj: Any) -> bool:
    lesson = _get_lesson(obj)

    if lesson is None:
        return False

    return getattr(lesson, "teacher_id", None) == getattr(user, "id", None)


def _is_student_owner(user: Any, obj: Any) -> bool:
    student_id = getattr(obj, "student_id", None)

    if student_id is None:
        return False

    return student_id == getattr(user, "id", None)


class IsJournalAdmin(BasePermission):
    """Полный доступ только администраторам и методистам."""

    def has_permission(self, request, view) -> bool:  # noqa: ANN001
        return _is_admin(request.user)

    def has_object_permission(self, request, view, obj) -> bool:  # noqa: ANN001
        return _is_admin(request.user)


class IsJournalTeacherOrAdmin(BasePermission):
    """Доступ преподавателям, администраторам и методистам."""

    def has_permission(self, request, view) -> bool:  # noqa: ANN001
        return _is_teacher(request.user)

    def has_object_permission(self, request, view, obj) -> bool:  # noqa: ANN001
        if _is_admin(request.user):
            return True

        if request.method in SAFE_METHODS:
            return _is_teacher(request.user)

        return _is_lesson_teacher(request.user, obj)


class IsLessonTeacherOrAdmin(BasePermission):
    """Изменять объект может преподаватель занятия или администратор."""

    def has_permission(self, request, view) -> bool:  # noqa: ANN001
        return _is_teacher(request.user)

    def has_object_permission(self, request, view, obj) -> bool:  # noqa: ANN001
        if _is_admin(request.user):
            return True

        return _is_lesson_teacher(request.user, obj)


class IsStudentJournalOwnerOrTeacherOrAdmin(BasePermission):
    """
    Студент видит свои данные.
    Преподаватель видит журнал.
    Администратор имеет полный доступ.
    """

    def has_permission(self, request, view) -> bool:  # noqa: ANN001
        return _is_authenticated(request.user)

    def has_object_permission(self, request, view, obj) -> bool:  # noqa: ANN001
        if _is_admin(request.user):
            return True

        if _is_teacher(request.user):
            if request.method in SAFE_METHODS:
                return True

            return _is_lesson_teacher(request.user, obj)

        return request.method in SAFE_METHODS and _is_student_owner(request.user, obj)


class IsJournalReadOnly(BasePermission):
    """Только чтение для авторизованных пользователей."""

    def has_permission(self, request, view) -> bool:  # noqa: ANN001
        return _is_authenticated(request.user) and request.method in SAFE_METHODS

    def has_object_permission(self, request, view, obj) -> bool:  # noqa: ANN001
        return _is_authenticated(request.user) and request.method in SAFE_METHODS
