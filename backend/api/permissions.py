from __future__ import annotations

from rest_framework.permissions import SAFE_METHODS, BasePermission


class ReadOnlyOrAdmin(BasePermission):
    def has_permission(self, request, view) -> bool:
        if request.method in SAFE_METHODS:
            return True
        return bool(
            request.user and request.user.is_authenticated and request.user.is_staff
        )


class IsAuthenticatedAndActive(BasePermission):
    def has_permission(self, request, view) -> bool:
        return bool(
            request.user and request.user.is_authenticated and request.user.is_active
        )


class HasRole(BasePermission):
    required_roles: tuple[str, ...] = ()

    def has_permission(self, request, view) -> bool:
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if user.is_superuser:
            return True

        if not hasattr(user, "user_roles"):
            return False

        user_roles = set(user.user_roles.values_list("role__code", flat=True))
        return bool(user_roles.intersection(self.required_roles))


class IsAdminRole(HasRole):
    required_roles = ("admin",)


class IsTeacherRole(HasRole):
    required_roles = ("teacher",)


class IsStudentRole(HasRole):
    required_roles = ("student",)


class IsParentRole(HasRole):
    required_roles = ("parent",)
