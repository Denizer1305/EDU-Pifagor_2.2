from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from apps.users.models import Role, UserRole


def _has_field(model, field_name: str) -> bool:
    return field_name in {field.name for field in model._meta.get_fields()}


def get_role_by_code(role_code: str) -> Role:
    role_code = (role_code or "").strip().lower()
    role = Role.objects.filter(code=role_code, is_active=True).first()
    if not role:
        raise ValidationError({"role": _("Активная роль с таким кодом не найдена.")})
    return role


def list_user_role_codes(user) -> list[str]:
    if not user or not user.is_authenticated:
        return []

    if user.is_superuser:
        return ["admin"]

    queryset = user.user_roles.all()
    if _has_field(UserRole, "is_active"):
        queryset = queryset.filter(is_active=True)

    return list(queryset.values_list("role__code", flat=True))


def user_has_role(user, role_code: str) -> bool:
    role_code = (role_code or "").strip().lower()

    if not user or not user.is_authenticated:
        return False

    if user.is_superuser and role_code == "admin":
        return True

    queryset = user.user_roles.filter(role__code=role_code)
    if _has_field(UserRole, "is_active"):
        queryset = queryset.filter(is_active=True)

    return queryset.exists()


@transaction.atomic
def assign_role_to_user(user, role_code: str) -> UserRole:
    role = get_role_by_code(role_code)

    user_role, created = UserRole.objects.get_or_create(
        user=user,
        role=role,
    )

    if not created and _has_field(UserRole, "is_active") and not user_role.is_active:
        user_role.is_active = True
        update_fields = ["is_active"]
        if _has_field(UserRole, "updated_at"):
            update_fields.append("updated_at")
        user_role.save(update_fields=update_fields)

    return user_role


@transaction.atomic
def remove_role_from_user(user, role_code: str) -> None:
    role_code = (role_code or "").strip().lower()
    queryset = UserRole.objects.filter(user=user, role__code=role_code)

    if _has_field(UserRole, "is_active"):
        for user_role in queryset:
            if user_role.is_active:
                user_role.is_active = False
                update_fields = ["is_active"]
                if _has_field(UserRole, "updated_at"):
                    update_fields.append("updated_at")
                user_role.save(update_fields=update_fields)
        return

    queryset.delete()
