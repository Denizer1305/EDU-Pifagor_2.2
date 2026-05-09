from __future__ import annotations

import logging
from datetime import date, time
from typing import Any

from django.core.exceptions import ValidationError
from django.db import transaction

from apps.journal.models import JournalLesson
from apps.journal.models.choices import JournalLessonStatus

logger = logging.getLogger(__name__)


@transaction.atomic
def create_journal_lesson(
    *,
    course,
    group,
    date: date,
    planned_topic: str,
    teacher=None,
    course_lesson=None,
    lesson_number: int | None = None,
    started_at: time | None = None,
    ended_at: time | None = None,
    actual_topic: str = "",
    homework: str = "",
    status: str = JournalLessonStatus.PLANNED,
    teacher_comment: str = "",
) -> JournalLesson:
    """Создаёт занятие в журнале."""

    logger.info(
        "create_journal_lesson started course_id=%s group_id=%s date=%s",
        getattr(course, "id", None),
        getattr(group, "id", None),
        date,
    )

    lesson = JournalLesson(
        course=course,
        group=group,
        teacher=teacher,
        course_lesson=course_lesson,
        lesson_number=lesson_number,
        date=date,
        started_at=started_at,
        ended_at=ended_at,
        planned_topic=planned_topic,
        actual_topic=actual_topic,
        homework=homework,
        status=status,
        teacher_comment=teacher_comment,
    )

    _validate_lesson_time(lesson)

    lesson.full_clean()
    lesson.save()

    logger.info("create_journal_lesson completed lesson_id=%s", lesson.id)
    return lesson


@transaction.atomic
def update_journal_lesson(
    lesson: JournalLesson,
    **fields: Any,
) -> JournalLesson:
    """Обновляет занятие журнала."""

    logger.info("update_journal_lesson started lesson_id=%s", lesson.id)

    for field_name, value in fields.items():
        setattr(lesson, field_name, value)

    _validate_lesson_time(lesson)

    lesson.full_clean()
    lesson.save()

    logger.info("update_journal_lesson completed lesson_id=%s", lesson.id)
    return lesson


@transaction.atomic
def mark_lesson_conducted(
    lesson: JournalLesson,
    *,
    actual_topic: str | None = None,
    homework: str | None = None,
    teacher_comment: str | None = None,
) -> JournalLesson:
    """Отмечает занятие как проведённое."""

    update_fields: dict[str, Any] = {
        "status": JournalLessonStatus.CONDUCTED,
    }

    if actual_topic is not None:
        update_fields["actual_topic"] = actual_topic

    if homework is not None:
        update_fields["homework"] = homework

    if teacher_comment is not None:
        update_fields["teacher_comment"] = teacher_comment

    return update_journal_lesson(lesson, **update_fields)


@transaction.atomic
def cancel_journal_lesson(
    lesson: JournalLesson,
    *,
    reason: str = "",
) -> JournalLesson:
    """Отменяет занятие."""

    return update_journal_lesson(
        lesson,
        status=JournalLessonStatus.CANCELLED,
        teacher_comment=reason or lesson.teacher_comment,
    )


def _validate_lesson_time(lesson: JournalLesson) -> None:
    """Проверяет корректность времени занятия."""

    if lesson.started_at and lesson.ended_at and lesson.started_at >= lesson.ended_at:
        raise ValidationError(
            {
                "ended_at": "Время окончания занятия должно быть позже времени начала.",
            }
        )
