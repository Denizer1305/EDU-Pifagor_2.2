from __future__ import annotations

from typing import Any

from django.utils import timezone

from apps.schedule.models import ScheduleChange, ScheduledLesson


def create_schedule_change(
    *,
    lesson: ScheduledLesson,
    change_type: str,
    created_by=None,
    old_values: dict[str, Any] | None = None,
    new_values: dict[str, Any] | None = None,
    comment: str = "",
) -> ScheduleChange:
    return ScheduleChange.objects.create(
        lesson=lesson,
        change_type=change_type,
        old_values=old_values or {},
        new_values=new_values or {},
        comment=comment,
        created_by=created_by,
        created_at=timezone.now(),
    )


def log_lesson_created(
    *,
    lesson: ScheduledLesson,
    created_by=None,
    comment: str = "",
) -> ScheduleChange:
    return create_schedule_change(
        lesson=lesson,
        change_type="created",
        created_by=created_by,
        new_values={
            "date": lesson.date.isoformat() if lesson.date else None,
            "starts_at": lesson.starts_at.isoformat() if lesson.starts_at else None,
            "ends_at": lesson.ends_at.isoformat() if lesson.ends_at else None,
            "teacher_id": lesson.teacher_id,
            "room_id": lesson.room_id,
            "status": lesson.status,
        },
        comment=comment,
    )


def log_lesson_updated(
    *,
    lesson: ScheduledLesson,
    old_values: dict[str, Any],
    new_values: dict[str, Any],
    created_by=None,
    comment: str = "",
) -> ScheduleChange:
    return create_schedule_change(
        lesson=lesson,
        change_type="updated",
        created_by=created_by,
        old_values=old_values,
        new_values=new_values,
        comment=comment,
    )


def log_lesson_cancelled(
    *,
    lesson: ScheduledLesson,
    old_status: str,
    created_by=None,
    comment: str = "",
) -> ScheduleChange:
    return create_schedule_change(
        lesson=lesson,
        change_type="cancelled",
        created_by=created_by,
        old_values={"status": old_status},
        new_values={"status": lesson.status},
        comment=comment,
    )


def log_lesson_rescheduled(
    *,
    lesson: ScheduledLesson,
    old_values: dict[str, Any],
    created_by=None,
    comment: str = "",
) -> ScheduleChange:
    return create_schedule_change(
        lesson=lesson,
        change_type="rescheduled",
        created_by=created_by,
        old_values=old_values,
        new_values={
            "date": lesson.date.isoformat() if lesson.date else None,
            "starts_at": lesson.starts_at.isoformat() if lesson.starts_at else None,
            "ends_at": lesson.ends_at.isoformat() if lesson.ends_at else None,
            "time_slot_id": lesson.time_slot_id,
        },
        comment=comment,
    )


def log_teacher_replaced(
    *,
    lesson: ScheduledLesson,
    old_teacher_id: int | None,
    created_by=None,
    comment: str = "",
) -> ScheduleChange:
    return create_schedule_change(
        lesson=lesson,
        change_type="teacher_replaced",
        created_by=created_by,
        old_values={"teacher_id": old_teacher_id},
        new_values={"teacher_id": lesson.teacher_id},
        comment=comment,
    )


def log_room_changed(
    *,
    lesson: ScheduledLesson,
    old_room_id: int | None,
    created_by=None,
    comment: str = "",
) -> ScheduleChange:
    return create_schedule_change(
        lesson=lesson,
        change_type="room_changed",
        created_by=created_by,
        old_values={"room_id": old_room_id},
        new_values={"room_id": lesson.room_id},
        comment=comment,
    )
