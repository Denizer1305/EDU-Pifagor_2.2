from __future__ import annotations

from rest_framework.permissions import BasePermission

from apps.users.constants import ROLE_ADMIN


def _get_user_role_codes(user) -> set[str]:
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
    if not user or not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    return ROLE_ADMIN in _get_user_role_codes(user)


class IsAdminOrSuperuser(BasePermission):
    message = "У вас нет прав администратора."

    def has_permission(self, request, view) -> bool:
        return is_admin_user(request.user)


class IsFeedbackOwnerOrAdmin(BasePermission):
    message = "У вас нет прав на доступ к этому обращению."

    def has_permission(self, request, view) -> bool:
        user = request.user
        return bool(user and user.is_authenticated)

    def has_object_permission(self, request, view, obj) -> bool:
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if is_admin_user(user):
            return True

        return getattr(obj, "user_id", None) == user.id
