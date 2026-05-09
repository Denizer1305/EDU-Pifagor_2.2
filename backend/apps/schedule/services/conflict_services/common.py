from __future__ import annotations

from datetime import date, time

from django.db.models import QuerySet

from apps.schedule.constants import (
    ConflictSeverity,
    ConflictStatus,
    ScheduleStatus,
)
from apps.schedule.models import ScheduleConflict, ScheduledLesson, SchedulePattern

IGNORED_LESSON_STATUSES = (
    ScheduleStatus.CANCELLED,
    ScheduleStatus.ARCHIVED,
)


def time_range_overlaps(
    first_starts_at: time,
    first_ends_at: time,
    second_starts_at: time,
    second_ends_at: time,
) -> bool:
    return first_starts_at < second_ends_at and first_ends_at > second_starts_at


def get_lesson_overlap_queryset(lesson: ScheduledLesson) -> QuerySet[ScheduledLesson]:
    queryset = ScheduledLesson.objects.filter(
        organization=lesson.organization,
        date=lesson.date,
        starts_at__lt=lesson.ends_at,
        ends_at__gt=lesson.starts_at,
    ).exclude(status__in=IGNORED_LESSON_STATUSES)

    if lesson.pk:
        queryset = queryset.exclude(pk=lesson.pk)

    return queryset


def get_pattern_time_range(pattern: SchedulePattern) -> tuple[time, time]:
    starts_at = pattern.starts_at or pattern.time_slot.starts_at
    ends_at = pattern.ends_at or pattern.time_slot.ends_at
    return starts_at, ends_at


def get_pattern_overlap_queryset(pattern: SchedulePattern) -> QuerySet[SchedulePattern]:
    return SchedulePattern.objects.filter(
        organization=pattern.organization,
        academic_year=pattern.academic_year,
        weekday=pattern.weekday,
        is_active=True,
    ).exclude(pk=pattern.pk)


def create_conflict(
    *,
    organization,
    conflict_type: str,
    message: str,
    severity: str = ConflictSeverity.ERROR,
    lesson: ScheduledLesson | None = None,
    pattern: SchedulePattern | None = None,
    related_lesson: ScheduledLesson | None = None,
    related_pattern: SchedulePattern | None = None,
    teacher=None,
    room=None,
    group=None,
    group_id: int | None = None,
    conflict_date: date | None = None,
    starts_at: time | None = None,
    ends_at: time | None = None,
) -> ScheduleConflict:
    conflict = ScheduleConflict(
        organization=organization,
        conflict_type=conflict_type,
        severity=severity,
        status=ConflictStatus.OPEN,
        lesson=lesson,
        pattern=pattern,
        related_lesson=related_lesson,
        related_pattern=related_pattern,
        teacher=teacher,
        room=room,
        group=group,
        group_id=group_id,
        date=conflict_date,
        starts_at=starts_at,
        ends_at=ends_at,
        message=message,
    )
    conflict.full_clean()
    conflict.save()
    return conflict
