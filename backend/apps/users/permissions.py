from __future__ import annotations

from rest_framework.permissions import SAFE_METHODS, BasePermission

from apps.users.constants import ROLE_ADMIN, ROLE_PARENT, ROLE_STUDENT, ROLE_TEACHER


def _get_user_role_codes(user) -> set[str]:
    """Возвращает множество кодов ролей пользователя."""
    if not user or not user.is_authenticated:
        return set()

    if not hasattr(user, "user_roles"):
        return set()

    return set(user.user_roles.values_list("role__code", flat=True))


class IsSelfOrAdmin(BasePermission):
    """
    Доступ владельцу объекта или администратору.
    Объект может быть User или моделью с полем user.
    """

    def has_object_permission(self, request, view, obj) -> bool:
        """Проверяет доступ к конкретному объекту."""
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if user.is_superuser:
            return True

        role_codes = _get_user_role_codes(user)
        if ROLE_ADMIN in role_codes:
            return True

        target_user = getattr(obj, "user", obj)
        return target_user == user


class CanManageUserRoles(BasePermission):
    """
    Управлять пользователями и ролями могут:
    - superuser
    - пользователь с бизнес-ролью admin
    """

    message = "У вас нет прав на управление пользователями и ролями."

    def has_permission(self, request, view) -> bool:
        """Проверяет доступ на уровне запроса."""
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if user.is_superuser:
            return True

        role_codes = _get_user_role_codes(user)
        return ROLE_ADMIN in role_codes


class IsTeacherProfileOwnerOrAdmin(BasePermission):
    """
    Доступ к teacher_profile:
    - владельцу teacher_profile
    - superuser
    - пользователю с ролью admin
    """

    message = "У вас нет прав на управление профилем преподавателя."

    def has_permission(self, request, view) -> bool:
        """Проверяет доступ на уровне запроса."""
        user = request.user
        return bool(user and user.is_authenticated)

    def has_object_permission(self, request, view, obj) -> bool:
        """Проверяет доступ к конкретному объекту."""
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if user.is_superuser:
            return True

        role_codes = _get_user_role_codes(user)
        if ROLE_ADMIN in role_codes:
            return True

        return getattr(obj, "user_id", None) == user.id


class IsParentProfileOwnerOrAdmin(BasePermission):
    """
    Доступ к parent_profile:
    - владельцу parent_profile
    - superuser
    - пользователю с ролью admin
    """

    message = "У вас нет прав на управление профилем родителя."

    def has_permission(self, request, view) -> bool:
        """Проверяет доступ на уровне запроса."""
        user = request.user
        return bool(user and user.is_authenticated)

    def has_object_permission(self, request, view, obj) -> bool:
        """Проверяет доступ к конкретному объекту."""
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if user.is_superuser:
            return True

        role_codes = _get_user_role_codes(user)
        if ROLE_ADMIN in role_codes:
            return True

        return getattr(obj, "user_id", None) == user.id
