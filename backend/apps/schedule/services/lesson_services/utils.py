from __future__ import annotations

from datetime import date

from apps.schedule.models import ScheduledLesson


def weekday_from_date(value: date) -> int:
    return value.isoweekday()


def apply_time_slot_defaults(lesson: ScheduledLesson) -> None:
    if not lesson.time_slot_id:
        return

    if not lesson.starts_at:
        lesson.starts_at = lesson.time_slot.starts_at

    if not lesson.ends_at:
        lesson.ends_at = lesson.time_slot.ends_at
