from __future__ import annotations

from rest_framework.permissions import BasePermission

from apps.users.constants import ROLE_ADMIN


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


def _is_admin(user) -> bool:
    """Проверяет, является ли пользователь администратором."""

    if not user or not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    return ROLE_ADMIN in _get_user_role_codes(user)


class IsAdminOrSuperuser(BasePermission):
    """Доступ только для администратора или superuser."""

    message = "У вас нет прав администратора."

    def has_permission(self, request, view) -> bool:
        return _is_admin(request.user)
