from __future__ import annotations

from datetime import date
from typing import Any

from apps.organizations.models import Group
from apps.schedule.models import ScheduledLesson, ScheduleRoom
from apps.users.models import User


def _get_export_lessons_queryset() -> Any:
    return ScheduledLesson.objects.select_related(
        "organization",
        "academic_year",
        "education_period",
        "time_slot",
        "group",
        "subject",
        "teacher",
        "room",
        "course",
        "course_lesson",
    )


def _apply_period_filter(
    queryset: Any, *, starts_on: date | None, ends_on: date | None
) -> Any:
    if starts_on:
        queryset = queryset.filter(date__gte=starts_on)

    if ends_on:
        queryset = queryset.filter(date__lte=ends_on)

    return queryset


def _serialize_lesson(lesson: ScheduledLesson) -> dict[str, Any]:
    return {
        "id": lesson.id,
        "date": lesson.date,
        "weekday": lesson.weekday,
        "lesson_number": lesson.time_slot.number if lesson.time_slot_id else None,
        "starts_at": lesson.starts_at,
        "ends_at": lesson.ends_at,
        "group": str(lesson.group) if lesson.group_id else "",
        "subject": str(lesson.subject) if lesson.subject_id else "",
        "teacher": str(lesson.teacher) if lesson.teacher_id else "",
        "room": str(lesson.room) if lesson.room_id else "",
        "course": str(lesson.course) if lesson.course_id else "",
        "course_lesson": str(lesson.course_lesson) if lesson.course_lesson_id else "",
        "lesson_type": lesson.lesson_type,
        "status": lesson.status,
        "is_public": lesson.is_public,
    }


def export_group_schedule(
    group: Group,
    *,
    starts_on: date | None = None,
    ends_on: date | None = None,
) -> list[dict[str, Any]]:
    lessons = _get_export_lessons_queryset().filter(group=group)
    lessons = _apply_period_filter(lessons, starts_on=starts_on, ends_on=ends_on)

    return [
        _serialize_lesson(lesson)
        for lesson in lessons.order_by("date", "starts_at", "time_slot__number", "id")
    ]


def export_teacher_schedule(
    teacher: User,
    *,
    starts_on: date | None = None,
    ends_on: date | None = None,
) -> list[dict[str, Any]]:
    lessons = _get_export_lessons_queryset().filter(teacher=teacher)
    lessons = _apply_period_filter(lessons, starts_on=starts_on, ends_on=ends_on)

    return [
        _serialize_lesson(lesson)
        for lesson in lessons.order_by("date", "starts_at", "time_slot__number", "id")
    ]


def export_room_schedule(
    room: ScheduleRoom,
    *,
    starts_on: date | None = None,
    ends_on: date | None = None,
) -> list[dict[str, Any]]:
    lessons = _get_export_lessons_queryset().filter(room=room)
    lessons = _apply_period_filter(lessons, starts_on=starts_on, ends_on=ends_on)

    return [
        _serialize_lesson(lesson)
        for lesson in lessons.order_by("date", "starts_at", "time_slot__number", "id")
    ]


def export_period_schedule(
    *,
    organization_id: int,
    education_period_id: int,
    starts_on: date | None = None,
    ends_on: date | None = None,
) -> list[dict[str, Any]]:
    lessons = _get_export_lessons_queryset().filter(
        organization_id=organization_id,
        education_period_id=education_period_id,
    )
    lessons = _apply_period_filter(lessons, starts_on=starts_on, ends_on=ends_on)

    return [
        _serialize_lesson(lesson)
        for lesson in lessons.order_by("date", "starts_at", "time_slot__number", "id")
    ]
