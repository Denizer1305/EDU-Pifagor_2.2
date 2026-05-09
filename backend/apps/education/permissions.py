from __future__ import annotations

from rest_framework.permissions import SAFE_METHODS, BasePermission

from apps.users.constants import ROLE_ADMIN, ROLE_TEACHER


def _get_user_role_codes(user) -> set[str]:
    if not user or not user.is_authenticated:
        return set()

    if user.is_superuser:
        return {ROLE_ADMIN}

    if not hasattr(user, "user_roles"):
        return set()

    return set(user.user_roles.values_list("role__code", flat=True))


class IsAdminOrReadOnly(BasePermission):
    """
    Чтение доступно авторизованным пользователям.
    Изменение доступно только администраторам.
    """

    message = "У вас нет прав на изменение академической структуры."

    def has_permission(self, request, view) -> bool:
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if request.method in SAFE_METHODS:
            return True

        role_codes = _get_user_role_codes(user)
        return ROLE_ADMIN in role_codes or user.is_superuser


class IsAdminOnly(BasePermission):
    """
    Полный доступ только для администратора.
    """

    message = "У вас нет прав администратора."

    def has_permission(self, request, view) -> bool:
        user = request.user
        if not user or not user.is_authenticated:
            return False

        role_codes = _get_user_role_codes(user)
        return ROLE_ADMIN in role_codes or user.is_superuser


class IsTeacherOrAdminReadOnly(BasePermission):
    """
    Чтение доступно преподавателю и администратору.
    Изменение доступно только администратору.
    """

    message = "У вас нет прав для доступа к этому разделу."

    def has_permission(self, request, view) -> bool:
        user = request.user
        if not user or not user.is_authenticated:
            return False

        role_codes = _get_user_role_codes(user)

        if request.method in SAFE_METHODS:
            return (
                ROLE_ADMIN in role_codes
                or ROLE_TEACHER in role_codes
                or user.is_superuser
            )

        return ROLE_ADMIN in role_codes or user.is_superuser


class IsTeacherAssignmentOwnerOrAdmin(BasePermission):
    """
    Доступ к закреплению преподавателя:
    - самому преподавателю;
    - администратору.
    """

    message = "У вас нет прав на доступ к этому закреплению преподавателя."

    def has_permission(self, request, view) -> bool:
        user = request.user
        return bool(user and user.is_authenticated)

    def has_object_permission(self, request, view, obj) -> bool:
        user = request.user
        if not user or not user.is_authenticated:
            return False

        role_codes = _get_user_role_codes(user)
        if ROLE_ADMIN in role_codes or user.is_superuser:
            return True

        teacher = getattr(obj, "teacher", None)
        return teacher == user
