from __future__ import annotations

from typing import Any

from apps.organizations.models import Organization
from apps.schedule.constants import ConflictSeverity, ConflictStatus, ConflictType
from apps.schedule.models import ScheduleConflict, ScheduledLesson, SchedulePattern
from apps.schedule.tests.factories.lessons import create_scheduled_lesson


def create_schedule_conflict(
    *,
    organization: Organization | None = None,
    lesson: ScheduledLesson | None = None,
    pattern: SchedulePattern | None = None,
    conflict_type: str = ConflictType.TEACHER_OVERLAP,
    severity: str = ConflictSeverity.ERROR,
    status: str = ConflictStatus.OPEN,
    message: str = "Тестовый конфликт расписания",
    **extra_fields: Any,
) -> ScheduleConflict:
    lesson = lesson or create_scheduled_lesson()
    organization = organization or lesson.organization

    return ScheduleConflict.objects.create(
        organization=organization,
        lesson=lesson,
        pattern=pattern,
        conflict_type=conflict_type,
        severity=severity,
        status=status,
        message=message,
        **extra_fields,
    )
