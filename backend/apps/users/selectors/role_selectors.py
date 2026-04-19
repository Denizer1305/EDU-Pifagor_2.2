from __future__ import annotations

from apps.users.models import Role


def get_roles_queryset():
    """Возвращает данные по заданным критериям."""
    return Role.objects.filter(is_active=True)


def get_role_by_code(code: str) -> Role | None:
    """Возвращает данные по заданным критериям."""
    return Role.objects.filter(code=code, is_active=True).first()
