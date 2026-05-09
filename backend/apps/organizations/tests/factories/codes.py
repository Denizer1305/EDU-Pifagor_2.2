from __future__ import annotations

from apps.organizations.models import Group, Organization


def activate_teacher_registration_code(
    organization: Organization,
    raw_code: str = "TEACHER-CODE-123",
    *,
    expires_at=None,
) -> Organization:
    """Активирует тестовый код регистрации преподавателя."""

    organization.set_teacher_registration_code(
        raw_code=raw_code,
        expires_at=expires_at,
    )
    organization.save()
    return organization


def activate_group_join_code(
    group: Group,
    raw_code: str = "GROUP-CODE-123",
    *,
    expires_at=None,
) -> Group:
    """Активирует тестовый код присоединения к группе."""

    group.set_join_code(
        raw_code=raw_code,
        expires_at=expires_at,
    )
    group.save()
    return group
