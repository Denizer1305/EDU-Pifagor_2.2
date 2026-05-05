from __future__ import annotations

from django.db import transaction

from apps.journal.models import JournalLesson
from apps.schedule.constants import ScheduleStatus
from apps.schedule.models import ScheduledLesson


def _get_primary_group(lesson: ScheduledLesson):
    primary_group = getattr(lesson, "primary_group", None)

    if primary_group is not None:
        return primary_group

    audience = (
        lesson.audiences.select_related("group")
        .filter(group__isnull=False)
        .order_by("id")
        .first()
    )

    if audience is None:
        return None

    return audience.group


def _get_lesson_number(lesson: ScheduledLesson) -> int | None:
    if lesson.time_slot_id:
        return lesson.time_slot.number

    return None


def _get_journal_status(lesson: ScheduledLesson) -> str:
    if lesson.status == ScheduleStatus.CANCELLED:
        return JournalLesson.LessonStatus.CANCELLED

    if lesson.status == ScheduleStatus.RESCHEDULED:
        return JournalLesson.LessonStatus.RESCHEDULED

    if lesson.status == ScheduleStatus.PUBLISHED:
        return JournalLesson.LessonStatus.PLANNED

    return JournalLesson.LessonStatus.PLANNED


def create_journal_lesson_from_schedule(
    *,
    lesson: ScheduledLesson,
) -> JournalLesson:
    group = _get_primary_group(lesson)

    if group is None:
        msg = "Нельзя создать занятие журнала без группы."
        raise ValueError(msg)

    lesson_number = _get_lesson_number(lesson)

    lookup = {
        "course": lesson.course,
        "group": group,
        "date": lesson.date,
        "lesson_number": lesson_number,
    }

    defaults = {
        "teacher": lesson.teacher,
        "course_lesson": lesson.course_lesson,
        "started_at": lesson.starts_at,
        "ended_at": lesson.ends_at,
        "planned_topic": lesson.title,
        "status": _get_journal_status(lesson),
    }

    journal_lesson, _created = JournalLesson.objects.update_or_create(
        **lookup,
        defaults=defaults,
    )

    return journal_lesson


@transaction.atomic
def sync_schedule_to_journal(
    *,
    lesson: ScheduledLesson,
) -> JournalLesson:
    return create_journal_lesson_from_schedule(lesson=lesson)


@transaction.atomic
def sync_cancelled_lesson_to_journal(
    *,
    lesson: ScheduledLesson,
) -> JournalLesson:
    journal_lesson = create_journal_lesson_from_schedule(lesson=lesson)
    journal_lesson.status = JournalLesson.LessonStatus.CANCELLED
    journal_lesson.save(update_fields=("status", "updated_at"))

    return journal_lesson


@transaction.atomic
def sync_rescheduled_lesson_to_journal(
    *,
    lesson: ScheduledLesson,
) -> JournalLesson:
    journal_lesson = create_journal_lesson_from_schedule(lesson=lesson)

    journal_lesson.date = lesson.date
    journal_lesson.started_at = lesson.starts_at
    journal_lesson.ended_at = lesson.ends_at
    journal_lesson.status = JournalLesson.LessonStatus.RESCHEDULED
    journal_lesson.save(
        update_fields=(
            "date",
            "started_at",
            "ended_at",
            "status",
            "updated_at",
        )
    )

    return journal_lesson
