from __future__ import annotations

from django.db.models import Q
from django.utils import timezone

from apps.organizations.models import TeacherOrganization


def get_teacher_organizations_queryset(
    *,
    teacher_id: int | None = None,
    organization_id: int | None = None,
    is_primary: bool | None = None,
    is_active: bool | None = None,
    current_only: bool = False,
):
    """Возвращает связи преподавателей с организациями."""

    queryset = TeacherOrganization.objects.select_related(
        "teacher",
        "teacher__profile",
        "organization",
    ).all()

    if teacher_id is not None:
        queryset = queryset.filter(teacher_id=teacher_id)

    if organization_id is not None:
        queryset = queryset.filter(organization_id=organization_id)

    if is_primary is not None:
        queryset = queryset.filter(is_primary=is_primary)

    if is_active is not None:
        queryset = queryset.filter(is_active=is_active)

    if current_only:
        today = timezone.localdate()
        queryset = queryset.filter(
            is_active=True,
        ).filter(
            Q(starts_at__isnull=True) | Q(starts_at__lte=today),
            Q(ends_at__isnull=True) | Q(ends_at__gte=today),
        )

    return queryset.order_by(
        "teacher__profile__last_name",
        "teacher__profile__first_name",
        "organization__name",
    )


def get_active_teacher_organizations_queryset(
    *,
    teacher_id: int | None = None,
    organization_id: int | None = None,
):
    """Возвращает актуальные связи преподавателей с организациями."""

    return get_teacher_organizations_queryset(
        teacher_id=teacher_id,
        organization_id=organization_id,
        current_only=True,
    )
