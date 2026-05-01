from __future__ import annotations

from apps.users.constants import ROLE_TEACHER


def _clean_str(value: str | None) -> str:
    """Очищает строковое значение."""

    return (value or "").strip()


def _user_has_teacher_role(user) -> bool:
    """Проверяет, может ли пользователь выступать преподавателем."""

    if not user or not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    if getattr(user, "registration_type", "") == "teacher":
        return True

    if not hasattr(user, "user_roles"):
        return False

    queryset = user.user_roles.filter(role__code=ROLE_TEACHER)
    model_fields = {field.name for field in queryset.model._meta.get_fields()}

    if "is_active" in model_fields:
        queryset = queryset.filter(is_active=True)

    return queryset.exists()
