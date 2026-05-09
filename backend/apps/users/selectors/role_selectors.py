from __future__ import annotations

from django.db.models import Q

from apps.users.models import Role, UserRole


def _has_field(model, field_name: str) -> bool:
    return field_name in {field.name for field in model._meta.get_fields()}


def get_roles_queryset(
    *,
    search: str | None = None,
    is_active: bool | None = None,
):
    queryset = Role.objects.all()

    if search:
        search = search.strip()
        queryset = queryset.filter(
            Q(code__icontains=search)
            | Q(name__icontains=search)
            | Q(description__icontains=search)
        )

    if is_active is not None:
        queryset = queryset.filter(is_active=is_active)

    return queryset.order_by("name", "code")


def get_role_by_code_selector(role_code: str):
    return Role.objects.filter(
        code=(role_code or "").strip().lower(),
    ).first()


def get_user_roles_queryset(
    *,
    user_id: int | None = None,
    role_code: str | None = None,
    is_active: bool | None = None,
):
    queryset = UserRole.objects.select_related(
        "user",
        "user__profile",
        "role",
    )

    if user_id is not None:
        queryset = queryset.filter(user_id=user_id)

    if role_code:
        queryset = queryset.filter(
            role__code=(role_code or "").strip().lower(),
        )

    if is_active is not None and _has_field(UserRole, "is_active"):
        queryset = queryset.filter(is_active=is_active)

    if _has_field(UserRole, "created_at"):
        return queryset.order_by("-created_at")
    if _has_field(UserRole, "assigned_at"):
        return queryset.order_by("-assigned_at")
    return queryset.order_by("-id")
