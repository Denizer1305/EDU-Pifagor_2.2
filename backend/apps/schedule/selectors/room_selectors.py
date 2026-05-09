from __future__ import annotations

from django.db.models import QuerySet

from apps.schedule.models import ScheduleRoom


def get_room_queryset() -> QuerySet[ScheduleRoom]:
    return ScheduleRoom.objects.select_related(
        "organization",
        "department",
    )


def get_active_rooms(*, organization_id: int | None = None) -> QuerySet[ScheduleRoom]:
    queryset = get_room_queryset().filter(is_active=True)

    if organization_id is not None:
        queryset = queryset.filter(organization_id=organization_id)

    return queryset


def get_rooms_for_organization(*, organization_id: int) -> QuerySet[ScheduleRoom]:
    return get_room_queryset().filter(organization_id=organization_id)


def get_room_by_id(*, room_id: int) -> ScheduleRoom:
    return get_room_queryset().get(id=room_id)


def get_rooms_by_type(
    *,
    organization_id: int,
    room_type: str,
    active_only: bool = True,
) -> QuerySet[ScheduleRoom]:
    queryset = get_rooms_for_organization(organization_id=organization_id).filter(
        room_type=room_type,
    )

    if active_only:
        queryset = queryset.filter(is_active=True)

    return queryset
