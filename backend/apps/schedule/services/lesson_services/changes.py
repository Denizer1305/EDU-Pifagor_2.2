from __future__ import annotations

from datetime import date, time

from apps.schedule.models import ScheduleChange, ScheduledLesson


def create_lesson_change(
    *,
    lesson: ScheduledLesson,
    change_type: str,
    changed_by=None,
    reason: str = "",
    comment: str = "",
    old_date: date | None = None,
    new_date: date | None = None,
    old_time_slot=None,
    new_time_slot=None,
    old_starts_at: time | None = None,
    new_starts_at: time | None = None,
    old_ends_at: time | None = None,
    new_ends_at: time | None = None,
    old_room=None,
    new_room=None,
    old_teacher=None,
    new_teacher=None,
) -> ScheduleChange:
    change = ScheduleChange(
        scheduled_lesson=lesson,
        change_type=change_type,
        old_date=old_date,
        new_date=new_date,
        old_time_slot=old_time_slot,
        new_time_slot=new_time_slot,
        old_starts_at=old_starts_at,
        new_starts_at=new_starts_at,
        old_ends_at=old_ends_at,
        new_ends_at=new_ends_at,
        old_room=old_room,
        new_room=new_room,
        old_teacher=old_teacher,
        new_teacher=new_teacher,
        reason=reason,
        changed_by=changed_by,
        comment=comment,
    )
    change.full_clean()
    change.save()
    return change
