from __future__ import annotations

from collections.abc import Iterable
from datetime import date

from apps.schedule.models import ScheduleConflict, ScheduledLesson

from .common import IGNORED_LESSON_STATUSES
from .lesson import detect_conflicts_for_lesson


def detect_conflicts_for_period(
    *,
    organization,
    starts_on: date,
    ends_on: date,
    lessons: Iterable[ScheduledLesson] | None = None,
) -> list[ScheduleConflict]:
    queryset = lessons or ScheduledLesson.objects.filter(
        organization=organization,
        date__gte=starts_on,
        date__lte=ends_on,
    ).exclude(status__in=IGNORED_LESSON_STATUSES)

    conflicts: list[ScheduleConflict] = []

    for lesson in queryset:
        conflicts.extend(detect_conflicts_for_lesson(lesson))

    return conflicts
