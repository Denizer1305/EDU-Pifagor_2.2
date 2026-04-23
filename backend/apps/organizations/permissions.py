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

    queryset = user.user_roles.all()
    model_fields = {field.name for field in queryset.model._meta.get_fields()}

    if "is_active" in model_fields:
        queryset = queryset.filter(is_active=True)

    return set(queryset.values_list("role__code", flat=True))


def _is_admin(user) -> bool:
    if not user or not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    return ROLE_ADMIN in _get_user_role_codes(user)


def _is_teacher(user) -> bool:
    if not user or not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    role_codes = _get_user_role_codes(user)
    return ROLE_TEACHER in role_codes or getattr(user, "registration_type", "") == "teacher"


class IsAdminOrReadOnly(BasePermission):
    """
    Чтение доступно авторизованным пользователям.
    Изменение доступно только администраторам.
    """

    message = "У вас нет прав на изменение организационных данных."

    def has_permission(self, request, view) -> bool:
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if request.method in SAFE_METHODS:
            return True

        return _is_admin(user)


class IsAdminOnly(BasePermission):
    """
    Полный доступ только для администратора.
    """

    message = "У вас нет прав администратора."

    def has_permission(self, request, view) -> bool:
        return _is_admin(request.user)


class IsTeacherOrAdminReadOnly(BasePermission):
    """
    Чтение доступно преподавателям и администраторам.
    Изменение доступно только администраторам.
    """

    message = "У вас нет прав для доступа к этому разделу."

    def has_permission(self, request, view) -> bool:
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if request.method in SAFE_METHODS:
            return _is_admin(user) or _is_teacher(user)

        return _is_admin(user)


class IsTeacherOwnerOrAdmin(BasePermission):
    """
    Доступ к связям преподавателя:
    - самому преподавателю
    - администратору
    """

    message = "У вас нет прав на управление этой связью преподавателя."

    def has_permission(self, request, view) -> bool:
        user = request.user
        return bool(user and user.is_authenticated)

    def has_object_permission(self, request, view, obj) -> bool:
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if _is_admin(user):
            return True

        teacher = getattr(obj, "teacher", None)
        return teacher == user
