from __future__ import annotations

from apps.users.constants import ROLE_ADMIN, ROLE_STUDENT, ROLE_TEACHER


def _get_user_role_codes(user) -> set[str]:
    """Возвращает активные коды ролей пользователя."""

    if not user or not user.is_authenticated:
        return set()

    if user.is_superuser:
        return {ROLE_ADMIN}

    if not hasattr(user, "user_roles"):
        return set()

    queryset = user.user_roles.all()
    model_fields = {field.name for field in queryset.model._meta.get_fields()}

    if "is_active" in model_fields:
        queryset = queryset.filter(is_active=True)

    return set(queryset.values_list("role__code", flat=True))


def is_admin_user(user) -> bool:
    """Проверяет, является ли пользователь администратором."""

    if not user or not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    return ROLE_ADMIN in _get_user_role_codes(user)


def is_teacher_user(user) -> bool:
    """Проверяет, является ли пользователь преподавателем."""

    if not user or not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    role_codes = _get_user_role_codes(user)
    return (
        ROLE_TEACHER in role_codes
        or getattr(user, "registration_type", "") == "teacher"
    )


def is_student_user(user) -> bool:
    """Проверяет, является ли пользователь студентом."""

    if not user or not user.is_authenticated:
        return False

    role_codes = _get_user_role_codes(user)
    return (
        ROLE_STUDENT in role_codes
        or getattr(user, "registration_type", "") == "student"
    )
