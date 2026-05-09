from __future__ import annotations

from datetime import date, time

from django.db import transaction
from django.utils.translation import gettext_lazy as _

from apps.schedule.constants import ScheduleChangeType, ScheduleStatus
from apps.schedule.models import ScheduledLesson
from apps.schedule.services.conflict_services import detect_conflicts_for_lesson

from .changes import create_lesson_change
from .utils import weekday_from_date


@transaction.atomic
def publish_lesson(
    lesson: ScheduledLesson,
    *,
    user=None,
    reason: str = "",
    comment: str = "",
) -> ScheduledLesson:
    lesson.status = ScheduleStatus.PUBLISHED
    lesson.is_public = True

    if user is not None:
        lesson.updated_by = user

    lesson.full_clean()
    lesson.save(update_fields=("status", "is_public", "updated_by", "updated_at"))

    create_lesson_change(
        lesson=lesson,
        change_type=ScheduleChangeType.PUBLISH,
        changed_by=user,
        reason=reason,
        comment=comment,
    )

    return lesson


@transaction.atomic
def cancel_lesson(
    lesson: ScheduledLesson,
    *,
    user=None,
    reason: str = "",
    comment: str = "",
) -> ScheduledLesson:
    old_date = lesson.date
    old_time_slot = lesson.time_slot
    old_starts_at = lesson.starts_at
    old_ends_at = lesson.ends_at
    old_room = lesson.room
    old_teacher = lesson.teacher

    lesson.status = ScheduleStatus.CANCELLED

    if user is not None:
        lesson.updated_by = user

    lesson.full_clean()
    lesson.save(update_fields=("status", "updated_by", "updated_at"))

    create_lesson_change(
        lesson=lesson,
        change_type=ScheduleChangeType.CANCEL,
        changed_by=user,
        reason=reason,
        comment=comment,
        old_date=old_date,
        old_time_slot=old_time_slot,
        old_starts_at=old_starts_at,
        old_ends_at=old_ends_at,
        old_room=old_room,
        old_teacher=old_teacher,
    )

    return lesson


@transaction.atomic
def reschedule_lesson(
    lesson: ScheduledLesson,
    *,
    new_date: date,
    new_time_slot=None,
    new_starts_at: time | None = None,
    new_ends_at: time | None = None,
    user=None,
    reason: str = "",
    comment: str = "",
    validate_conflicts: bool = True,
) -> ScheduledLesson:
    if lesson.is_locked:
        raise ValueError(_("Занятие заблокировано от изменений."))

    old_date = lesson.date
    old_time_slot = lesson.time_slot
    old_starts_at = lesson.starts_at
    old_ends_at = lesson.ends_at

    lesson.date = new_date
    lesson.weekday = weekday_from_date(new_date)

    if new_time_slot is not None:
        lesson.time_slot = new_time_slot
        lesson.starts_at = new_starts_at or new_time_slot.starts_at
        lesson.ends_at = new_ends_at or new_time_slot.ends_at
    else:
        if new_starts_at is not None:
            lesson.starts_at = new_starts_at

        if new_ends_at is not None:
            lesson.ends_at = new_ends_at

    lesson.status = ScheduleStatus.RESCHEDULED

    if user is not None:
        lesson.updated_by = user

    lesson.full_clean()
    lesson.save()

    create_lesson_change(
        lesson=lesson,
        change_type=ScheduleChangeType.RESCHEDULE,
        changed_by=user,
        reason=reason,
        comment=comment,
        old_date=old_date,
        new_date=lesson.date,
        old_time_slot=old_time_slot,
        new_time_slot=lesson.time_slot,
        old_starts_at=old_starts_at,
        new_starts_at=lesson.starts_at,
        old_ends_at=old_ends_at,
        new_ends_at=lesson.ends_at,
    )

    if validate_conflicts:
        detect_conflicts_for_lesson(lesson)

    return lesson


@transaction.atomic
def replace_teacher(
    lesson: ScheduledLesson,
    *,
    new_teacher,
    user=None,
    reason: str = "",
    comment: str = "",
    validate_conflicts: bool = True,
) -> ScheduledLesson:
    if lesson.is_locked:
        raise ValueError(_("Занятие заблокировано от изменений."))

    old_teacher = lesson.teacher

    lesson.teacher = new_teacher
    lesson.status = ScheduleStatus.REPLACED

    if user is not None:
        lesson.updated_by = user

    lesson.full_clean()
    lesson.save(update_fields=("teacher", "status", "updated_by", "updated_at"))

    create_lesson_change(
        lesson=lesson,
        change_type=ScheduleChangeType.REPLACE_TEACHER,
        changed_by=user,
        reason=reason,
        comment=comment,
        old_teacher=old_teacher,
        new_teacher=new_teacher,
    )

    if validate_conflicts:
        detect_conflicts_for_lesson(lesson)

    return lesson


@transaction.atomic
def change_room(
    lesson: ScheduledLesson,
    *,
    new_room,
    user=None,
    reason: str = "",
    comment: str = "",
    validate_conflicts: bool = True,
) -> ScheduledLesson:
    if lesson.is_locked:
        raise ValueError(_("Занятие заблокировано от изменений."))

    old_room = lesson.room

    lesson.room = new_room
    lesson.status = ScheduleStatus.MOVED

    if user is not None:
        lesson.updated_by = user

    lesson.full_clean()
    lesson.save(update_fields=("room", "status", "updated_by", "updated_at"))

    create_lesson_change(
        lesson=lesson,
        change_type=ScheduleChangeType.CHANGE_ROOM,
        changed_by=user,
        reason=reason,
        comment=comment,
        old_room=old_room,
        new_room=new_room,
    )

    if validate_conflicts:
        detect_conflicts_for_lesson(lesson)

    return lesson


@transaction.atomic
def lock_lesson(
    lesson: ScheduledLesson,
    *,
    user=None,
    reason: str = "",
    comment: str = "",
) -> ScheduledLesson:
    lesson.is_locked = True

    if user is not None:
        lesson.updated_by = user

    lesson.full_clean()
    lesson.save(update_fields=("is_locked", "updated_by", "updated_at"))

    create_lesson_change(
        lesson=lesson,
        change_type=ScheduleChangeType.LOCK,
        changed_by=user,
        reason=reason,
        comment=comment,
    )

    return lesson


@transaction.atomic
def unlock_lesson(
    lesson: ScheduledLesson,
    *,
    user=None,
    reason: str = "",
    comment: str = "",
) -> ScheduledLesson:
    lesson.is_locked = False

    if user is not None:
        lesson.updated_by = user

    lesson.full_clean()
    lesson.save(update_fields=("is_locked", "updated_by", "updated_at"))

    create_lesson_change(
        lesson=lesson,
        change_type=ScheduleChangeType.UNLOCK,
        changed_by=user,
        reason=reason,
        comment=comment,
    )

    return lesson
