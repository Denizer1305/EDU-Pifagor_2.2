from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any

from django.db import transaction
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from apps.journal.models import (
    AttendanceRecord,
    JournalGrade,
    JournalLesson,
    TopicProgress,
)
from apps.journal.tasks import (
    recalculate_group_journal_summary_task,
    recalculate_group_student_journal_summaries_task,
    recalculate_journal_summaries_for_lesson_task,
    recalculate_student_journal_summary_task,
    sync_topic_progress_for_course_group_task,
    sync_topic_progress_for_lesson_task,
)

logger = logging.getLogger(__name__)


def _enqueue_after_commit(task_func: Callable[..., Any], **kwargs: Any) -> None:
    """Ставит Celery-задачу после успешного commit транзакции."""

    transaction.on_commit(lambda: task_func.delay(**kwargs))


def _enqueue_lesson_summary_recalculation(lesson: JournalLesson | None) -> None:
    """Ставит пересчёт сводок по конкретному занятию."""

    if lesson is None or lesson.id is None:
        return

    _enqueue_after_commit(
        recalculate_journal_summaries_for_lesson_task,
        lesson_id=lesson.id,
    )


def _enqueue_course_group_recalculation(
    *,
    course_id: int | None,
    group_id: int | None,
) -> None:
    """Ставит пересчёт групповой и индивидуальных сводок курса/группы."""

    if course_id is None or group_id is None:
        return

    _enqueue_after_commit(
        recalculate_group_journal_summary_task,
        course_id=course_id,
        group_id=group_id,
    )
    _enqueue_after_commit(
        recalculate_group_student_journal_summaries_task,
        course_id=course_id,
        group_id=group_id,
    )


def _enqueue_student_summary_recalculation(
    *,
    lesson: JournalLesson | None,
    student_id: int | None,
) -> None:
    """Ставит пересчёт индивидуальной сводки студента и общей сводки группы."""

    if lesson is None or student_id is None:
        return

    _enqueue_after_commit(
        recalculate_student_journal_summary_task,
        course_id=lesson.course_id,
        group_id=lesson.group_id,
        student_id=student_id,
    )
    _enqueue_after_commit(
        recalculate_group_journal_summary_task,
        course_id=lesson.course_id,
        group_id=lesson.group_id,
    )


@receiver(post_save, sender=JournalLesson)
def journal_lesson_saved(
    sender,
    instance: JournalLesson,
    created: bool,
    raw: bool = False,
    **kwargs,
) -> None:
    """После изменения занятия синхронизирует темы и сводки журнала."""

    if raw:
        return

    _enqueue_after_commit(
        sync_topic_progress_for_lesson_task,
        lesson_id=instance.id,
    )
    _enqueue_lesson_summary_recalculation(instance)

    logger.debug(
        "JournalLesson post_save handled. lesson_id=%s created=%s",
        instance.id,
        created,
    )


@receiver(post_delete, sender=JournalLesson)
def journal_lesson_deleted(
    sender,
    instance: JournalLesson,
    **kwargs,
) -> None:
    """После удаления занятия пересчитывает сводки курса/группы и прогресс тем."""

    _enqueue_course_group_recalculation(
        course_id=instance.course_id,
        group_id=instance.group_id,
    )
    _enqueue_after_commit(
        sync_topic_progress_for_course_group_task,
        course_id=instance.course_id,
        group_id=instance.group_id,
    )

    logger.debug("JournalLesson post_delete handled. lesson_id=%s", instance.id)


@receiver(post_save, sender=AttendanceRecord)
def attendance_record_saved(
    sender,
    instance: AttendanceRecord,
    created: bool,
    raw: bool = False,
    **kwargs,
) -> None:
    """После изменения посещаемости пересчитывает сводки."""

    if raw:
        return

    _enqueue_student_summary_recalculation(
        lesson=instance.lesson,
        student_id=instance.student_id,
    )

    logger.debug(
        "AttendanceRecord post_save handled. attendance_id=%s created=%s",
        instance.id,
        created,
    )


@receiver(post_delete, sender=AttendanceRecord)
def attendance_record_deleted(
    sender,
    instance: AttendanceRecord,
    **kwargs,
) -> None:
    """После удаления посещаемости пересчитывает сводки."""

    _enqueue_student_summary_recalculation(
        lesson=instance.lesson,
        student_id=instance.student_id,
    )

    logger.debug("AttendanceRecord post_delete handled. attendance_id=%s", instance.id)


@receiver(post_save, sender=JournalGrade)
def journal_grade_saved(
    sender,
    instance: JournalGrade,
    created: bool,
    raw: bool = False,
    **kwargs,
) -> None:
    """После изменения оценки пересчитывает сводки."""

    if raw:
        return

    _enqueue_student_summary_recalculation(
        lesson=instance.lesson,
        student_id=instance.student_id,
    )

    logger.debug(
        "JournalGrade post_save handled. grade_id=%s created=%s",
        instance.id,
        created,
    )


@receiver(post_delete, sender=JournalGrade)
def journal_grade_deleted(
    sender,
    instance: JournalGrade,
    **kwargs,
) -> None:
    """После удаления оценки пересчитывает сводки."""

    _enqueue_student_summary_recalculation(
        lesson=instance.lesson,
        student_id=instance.student_id,
    )

    logger.debug("JournalGrade post_delete handled. grade_id=%s", instance.id)


@receiver(post_save, sender=TopicProgress)
def topic_progress_saved(
    sender,
    instance: TopicProgress,
    created: bool,
    raw: bool = False,
    **kwargs,
) -> None:
    """После изменения прогресса темы пересчитывает сводки."""

    if raw:
        return

    _enqueue_course_group_recalculation(
        course_id=instance.course_id,
        group_id=instance.group_id,
    )

    logger.debug(
        "TopicProgress post_save handled. progress_id=%s created=%s",
        instance.id,
        created,
    )


@receiver(post_delete, sender=TopicProgress)
def topic_progress_deleted(
    sender,
    instance: TopicProgress,
    **kwargs,
) -> None:
    """После удаления прогресса темы пересчитывает сводки."""

    _enqueue_course_group_recalculation(
        course_id=instance.course_id,
        group_id=instance.group_id,
    )

    logger.debug("TopicProgress post_delete handled. progress_id=%s", instance.id)
