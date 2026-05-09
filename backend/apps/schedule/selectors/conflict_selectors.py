from __future__ import annotations

from datetime import date

from django.db.models import QuerySet

from apps.schedule.constants import ConflictStatus
from apps.schedule.models import ScheduleConflict


def get_conflict_queryset() -> QuerySet[ScheduleConflict]:
    return ScheduleConflict.objects.select_related(
        "organization",
        "lesson",
        "pattern",
        "related_lesson",
        "related_pattern",
        "teacher",
        "room",
        "group",
        "resolved_by",
    )


def get_conflict_by_id(*, conflict_id: int) -> ScheduleConflict:
    return get_conflict_queryset().get(id=conflict_id)


def get_open_conflicts(
    *,
    organization_id: int | None = None,
) -> QuerySet[ScheduleConflict]:
    queryset = get_conflict_queryset().filter(status=ConflictStatus.OPEN)

    if organization_id is not None:
        queryset = queryset.filter(organization_id=organization_id)

    return queryset


def get_conflicts_for_lesson(*, lesson_id: int) -> QuerySet[ScheduleConflict]:
    return get_conflict_queryset().filter(lesson_id=lesson_id)


def get_conflicts_for_pattern(*, pattern_id: int) -> QuerySet[ScheduleConflict]:
    return get_conflict_queryset().filter(pattern_id=pattern_id)


def get_conflicts_for_teacher(
    *,
    teacher_id: int,
    starts_on: date | None = None,
    ends_on: date | None = None,
    open_only: bool = False,
) -> QuerySet[ScheduleConflict]:
    queryset = get_conflict_queryset().filter(teacher_id=teacher_id)

    if starts_on is not None:
        queryset = queryset.filter(date__gte=starts_on)

    if ends_on is not None:
        queryset = queryset.filter(date__lte=ends_on)

    if open_only:
        queryset = queryset.filter(status=ConflictStatus.OPEN)

    return queryset


def get_conflicts_for_room(
    *,
    room_id: int,
    starts_on: date | None = None,
    ends_on: date | None = None,
    open_only: bool = False,
) -> QuerySet[ScheduleConflict]:
    queryset = get_conflict_queryset().filter(room_id=room_id)

    if starts_on is not None:
        queryset = queryset.filter(date__gte=starts_on)

    if ends_on is not None:
        queryset = queryset.filter(date__lte=ends_on)

    if open_only:
        queryset = queryset.filter(status=ConflictStatus.OPEN)

    return queryset


def get_conflicts_for_group(
    *,
    group_id: int,
    starts_on: date | None = None,
    ends_on: date | None = None,
    open_only: bool = False,
) -> QuerySet[ScheduleConflict]:
    queryset = get_conflict_queryset().filter(group_id=group_id)

    if starts_on is not None:
        queryset = queryset.filter(date__gte=starts_on)

    if ends_on is not None:
        queryset = queryset.filter(date__lte=ends_on)

    if open_only:
        queryset = queryset.filter(status=ConflictStatus.OPEN)

    return queryset


def get_conflicts_for_period(
    *,
    organization_id: int,
    starts_on: date,
    ends_on: date,
    open_only: bool = False,
) -> QuerySet[ScheduleConflict]:
    queryset = get_conflict_queryset().filter(
        organization_id=organization_id,
        date__range=(starts_on, ends_on),
    )

    if open_only:
        queryset = queryset.filter(status=ConflictStatus.OPEN)

    return queryset
