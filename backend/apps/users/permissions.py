from rest_framework.permissions import SAFE_METHODS, BasePermission

from users.constants import ROLE_ADMIN


class IsSelfOrAdmin(BasePermission):
    """
    Доступ разрешен владельцу объекта или администратору.
    Предполагается, что объект содержит поле `user` или сам является User
    """

    def has_permission(self, request, view, obj) -> bool:
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if user.is_superuser:
            return True

        if hasattr(user, "users_roles"):
            role_codes = set(user.users_roles.values_list("role_code", flat=True))
            if ROLE_ADMIN in role_codes:
                return True

        target_user = getattr(obj, "user", obj)
        return target_user == user
