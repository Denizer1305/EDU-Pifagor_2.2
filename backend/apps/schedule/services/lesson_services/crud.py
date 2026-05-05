from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from django.db import transaction

from apps.schedule.models import ScheduledLesson
from apps.schedule.services.conflict_services import detect_conflicts_for_lesson

from .audiences import sync_lesson_audiences
from .utils import apply_time_slot_defaults, weekday_from_date


@transaction.atomic
def create_scheduled_lesson(
    *,
    audiences: Iterable[dict[str, Any]] | None = None,
    validate_conflicts: bool = True,
    **data,
) -> ScheduledLesson:
    lesson = ScheduledLesson(**data)
    lesson.weekday = lesson.weekday or weekday_from_date(lesson.date)

    apply_time_slot_defaults(lesson)

    lesson.full_clean()
    lesson.save()

    sync_lesson_audiences(lesson, audiences)

    if validate_conflicts:
        detect_conflicts_for_lesson(lesson)

    return lesson


@transaction.atomic
def update_scheduled_lesson(
    lesson: ScheduledLesson,
    *,
    audiences: Iterable[dict[str, Any]] | None = None,
    updated_by=None,
    validate_conflicts: bool = True,
    **data,
) -> ScheduledLesson:
    for field_name, value in data.items():
        setattr(lesson, field_name, value)

    if "date" in data:
        lesson.weekday = weekday_from_date(lesson.date)

    if "time_slot" in data or "time_slot_id" in data:
        apply_time_slot_defaults(lesson)

    if updated_by is not None:
        lesson.updated_by = updated_by

    lesson.full_clean()
    lesson.save()

    sync_lesson_audiences(lesson, audiences)

    if validate_conflicts:
        detect_conflicts_for_lesson(lesson)

    return lesson
