from __future__ import annotations

from datetime import date
from typing import Any

from apps.organizations.models import Group
from apps.schedule.models import ScheduledLesson, ScheduleRoom
from apps.users.models import User


def _get_report_lessons_queryset() -> Any:
    return ScheduledLesson.objects.select_related(
        "organization",
        "academic_year",
        "education_period",
        "pattern",
        "time_slot",
        "group",
        "subject",
        "teacher",
        "room",
        "course",
        "course_lesson",
        "journal_lesson",
    ).prefetch_related("audiences")


def _serialize_lesson_for_report(lesson: ScheduledLesson) -> dict[str, Any]:
    return {
        "id": lesson.id,
        "organization": lesson.organization_id,
        "academic_year": lesson.academic_year_id,
        "education_period": lesson.education_period_id,
        "pattern": lesson.pattern_id,
        "date": lesson.date,
        "weekday": lesson.weekday,
        "time_slot": lesson.time_slot_id,
        "starts_at": lesson.starts_at,
        "ends_at": lesson.ends_at,
        "group": lesson.group_id,
        "subject": lesson.subject_id,
        "teacher": lesson.teacher_id,
        "room": lesson.room_id,
        "course": lesson.course_id,
        "course_lesson": lesson.course_lesson_id,
        "lesson_type": lesson.lesson_type,
        "source_type": lesson.source_type,
        "status": lesson.status,
        "is_locked": lesson.is_locked,
        "is_public": lesson.is_public,
    }


def get_group_schedule_report(
    *,
    group: Group,
    starts_on: date,
    ends_on: date,
) -> dict[str, Any]:
    lessons = (
        _get_report_lessons_queryset()
        .filter(
            group=group,
            date__gte=starts_on,
            date__lte=ends_on,
        )
        .order_by("date", "starts_at", "time_slot__number", "id")
    )

    return {
        "group": group.id,
        "starts_on": starts_on,
        "ends_on": ends_on,
        "lessons_count": lessons.count(),
        "lessons": [_serialize_lesson_for_report(lesson) for lesson in lessons],
    }


def get_teacher_schedule_report(
    *,
    teacher: User,
    starts_on: date,
    ends_on: date,
) -> dict[str, Any]:
    lessons = (
        _get_report_lessons_queryset()
        .filter(
            teacher=teacher,
            date__gte=starts_on,
            date__lte=ends_on,
        )
        .order_by("date", "starts_at", "time_slot__number", "id")
    )

    return {
        "teacher": teacher.id,
        "starts_on": starts_on,
        "ends_on": ends_on,
        "lessons_count": lessons.count(),
        "lessons": [_serialize_lesson_for_report(lesson) for lesson in lessons],
    }


def get_room_schedule_report(
    *,
    room: ScheduleRoom,
    starts_on: date,
    ends_on: date,
) -> dict[str, Any]:
    lessons = (
        _get_report_lessons_queryset()
        .filter(
            room=room,
            date__gte=starts_on,
            date__lte=ends_on,
        )
        .order_by("date", "starts_at", "time_slot__number", "id")
    )

    return {
        "room": room.id,
        "starts_on": starts_on,
        "ends_on": ends_on,
        "lessons_count": lessons.count(),
        "lessons": [_serialize_lesson_for_report(lesson) for lesson in lessons],
    }
