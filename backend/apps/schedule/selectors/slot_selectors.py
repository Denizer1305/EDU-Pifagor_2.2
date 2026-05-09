from __future__ import annotations

from django.db.models import QuerySet

from apps.schedule.models import ScheduleTimeSlot


def get_time_slot_queryset() -> QuerySet[ScheduleTimeSlot]:
    return ScheduleTimeSlot.objects.select_related("organization")


def get_active_time_slots(
    *,
    organization_id: int | None = None,
) -> QuerySet[ScheduleTimeSlot]:
    queryset = get_time_slot_queryset().filter(is_active=True)

    if organization_id is not None:
        queryset = queryset.filter(organization_id=organization_id)

    return queryset


def get_time_slots_for_organization(
    *,
    organization_id: int,
    active_only: bool = True,
) -> QuerySet[ScheduleTimeSlot]:
    queryset = get_time_slot_queryset().filter(organization_id=organization_id)

    if active_only:
        queryset = queryset.filter(is_active=True)

    return queryset


def get_time_slots_by_education_level(
    *,
    organization_id: int,
    education_level: str,
    active_only: bool = True,
) -> QuerySet[ScheduleTimeSlot]:
    queryset = get_time_slots_for_organization(
        organization_id=organization_id,
        active_only=active_only,
    ).filter(education_level=education_level)

    return queryset


def get_time_slot_by_id(*, time_slot_id: int) -> ScheduleTimeSlot:
    return get_time_slot_queryset().get(id=time_slot_id)
