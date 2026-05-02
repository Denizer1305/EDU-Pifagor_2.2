from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from apps.journal.models import JournalLesson, LessonStatus

if TYPE_CHECKING:
    pass


def create_journal_lesson(
    *,
    course_id: int,
    group_id: int,
    teacher_id: int,
    lesson_date: date,
    planned_topic: str = "",
    actual_topic: str = "",
    homework: str = "",
    status: str = LessonStatus.PLANNED,
    teacher_comment: str = "",
    course_lesson_id: int | None = None,
    lesson_number: int | None = None,
    started_at=None,
    ended_at=None,
) -> JournalLesson:
    """
    Создаёт новое занятие в журнале.

    Проверяет, что дата не в будущем при статусе CONDUCTED.
    """
    if status == LessonStatus.CONDUCTED and lesson_date > date.today():
        raise ValidationError(
            _("Нельзя отметить как проведённое занятие с датой в будущем.")
        )

    lesson = JournalLesson(
        course_id=course_id,
        group_id=group_id,
        teacher_id=teacher_id,
        date=lesson_date,
        planned_topic=planned_topic,
        actual_topic=actual_topic,
        homework=homework,
        status=status,
        teacher_comment=teacher_comment,
        course_lesson_id=course_lesson_id,
        lesson_number=lesson_number,
        started_at=started_at,
        ended_at=ended_at,
    )
    lesson.full_clean()
    lesson.save()
    return lesson


def update_journal_lesson(
    *,
    lesson: JournalLesson,
    **kwargs,
) -> JournalLesson:
    """
    Обновляет поля занятия. Передаются только изменяемые поля.

    Допустимые поля: planned_topic, actual_topic, homework, status,
    teacher_comment, started_at, ended_at, lesson_number, course_lesson_id.
    """
    allowed_fields = {
        "planned_topic",
        "actual_topic",
        "homework",
        "status",
        "teacher_comment",
        "started_at",
        "ended_at",
        "lesson_number",
        "course_lesson_id",
        "date",
    }

    for field, value in kwargs.items():
        if field not in allowed_fields:
            raise ValueError(f"Поле '{field}' не разрешено для обновления.")
        setattr(lesson, field, value)

    lesson.full_clean()
    lesson.save(update_fields=list(kwargs.keys()) + ["updated_at"])
    return lesson


def delete_journal_lesson(*, lesson: JournalLesson) -> None:
    """
    Удаляет занятие из журнала.
    Каскадно удаляет записи посещаемости и оценки (через on_delete=CASCADE).
    """
    lesson.delete()


def conduct_lesson(
    *,
    lesson: JournalLesson,
    actual_topic: str = "",
    teacher_comment: str = "",
) -> JournalLesson:
    """
    Отмечает занятие как проведённое.
    Если фактическая тема не указана — подставляет плановую.
    """
    if lesson.date > date.today():
        raise ValidationError(_("Нельзя провести занятие с датой в будущем."))

    lesson.status = LessonStatus.CONDUCTED
    lesson.actual_topic = actual_topic or lesson.planned_topic
    if teacher_comment:
        lesson.teacher_comment = teacher_comment

    lesson.full_clean()
    lesson.save(
        update_fields=["status", "actual_topic", "teacher_comment", "updated_at"]
    )
    return lesson


def cancel_lesson(
    *,
    lesson: JournalLesson,
    teacher_comment: str = "",
) -> JournalLesson:
    """
    Отменяет занятие. Нельзя отменить уже проведённое.
    """
    if lesson.status == LessonStatus.CONDUCTED:
        raise ValidationError(_("Нельзя отменить уже проведённое занятие."))

    lesson.status = LessonStatus.CANCELLED
    if teacher_comment:
        lesson.teacher_comment = teacher_comment

    lesson.save(update_fields=["status", "teacher_comment", "updated_at"])
    return lesson
