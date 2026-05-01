from __future__ import annotations

from django.db.models import Q
from django.utils import timezone

from apps.organizations.models import GroupCurator


def get_group_curators_queryset(
    *,
    group_id: int | None = None,
    teacher_id: int | None = None,
    is_primary: bool | None = None,
    is_active: bool | None = None,
    current_only: bool = False,
):
    """Возвращает queryset кураторов групп."""

    queryset = GroupCurator.objects.select_related(
        "group",
        "group__organization",
        "group__department",
        "teacher",
        "teacher__profile",
    ).all()

    if group_id is not None:
        queryset = queryset.filter(group_id=group_id)

    if teacher_id is not None:
        queryset = queryset.filter(teacher_id=teacher_id)

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
        "-is_primary",
        "-is_active",
        "group__name",
        "teacher__profile__last_name",
        "teacher__profile__first_name",
    )


def get_active_group_curators_queryset(*, group_id: int | None = None):
    """Возвращает актуальных кураторов группы."""

    return get_group_curators_queryset(
        group_id=group_id,
        current_only=True,
    )
