from __future__ import annotations

from rest_framework.permissions import SAFE_METHODS, BasePermission

from apps.course.permissions.roles import (
    is_admin_user,
    is_teacher_user,
)


class IsAdminOnly(BasePermission):
    message = "У вас нет прав администратора."

    def has_permission(self, request, view) -> bool:
        return is_admin_user(request.user)


class IsTeacherOrAdmin(BasePermission):
    message = "Действие доступно только преподавателю или администратору."

    def has_permission(self, request, view) -> bool:
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and (is_teacher_user(user) or is_admin_user(user))
        )


class IsTeacherOrAdminReadOnly(BasePermission):
    message = "У вас нет прав для доступа к этому разделу."

    def has_permission(self, request, view) -> bool:
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if request.method in SAFE_METHODS:
            return is_teacher_user(user) or is_admin_user(user)

        return is_teacher_user(user) or is_admin_user(user)
