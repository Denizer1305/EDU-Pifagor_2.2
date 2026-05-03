from __future__ import annotations

import logging
from typing import Any

from celery import shared_task

from apps.journal.models import AttendanceRecord, JournalGrade, JournalLesson
from apps.journal.services.summary_services import recalculate_journal_summary
from apps.journal.services.topic_progress_services import (
    sync_topic_progress_for_course_group,
)

logger = logging.getLogger(__name__)


def _get_student_ids_for_course_group(*, course_id: int, group_id: int) -> set[int]:
    """Возвращает студентов, по которым уже есть записи посещаемости или оценки."""

    attendance_student_ids = AttendanceRecord.objects.filter(
        lesson__course_id=course_id,
        lesson__group_id=group_id,
    ).values_list("student_id", flat=True)

    grade_student_ids = JournalGrade.objects.filter(
        lesson__course_id=course_id,
        lesson__group_id=group_id,
    ).values_list("student_id", flat=True)

    return set(attendance_student_ids) | set(grade_student_ids)


@shared_task(name="journal.recalculate_student_journal_summary")
def recalculate_student_journal_summary_task(
    *,
    course_id: int,
    group_id: int,
    student_id: int,
) -> dict[str, Any]:
    """Пересчитывает сводку журнала для конкретного студента."""

    summary = recalculate_journal_summary(
        course_id=course_id,
        group_id=group_id,
        student_id=student_id,
    )

    logger.info(
        "Student journal summary recalculated. summary_id=%s course_id=%s "
        "group_id=%s student_id=%s",
        getattr(summary, "id", None),
        course_id,
        group_id,
        student_id,
    )

    return {
        "summary_id": getattr(summary, "id", None),
        "course_id": course_id,
        "group_id": group_id,
        "student_id": student_id,
    }


@shared_task(name="journal.recalculate_group_journal_summary")
def recalculate_group_journal_summary_task(
    *,
    course_id: int,
    group_id: int,
) -> dict[str, Any]:
    """Пересчитывает общую сводку журнала по курсу и группе."""

    summary = recalculate_journal_summary(
        course_id=course_id,
        group_id=group_id,
        student_id=None,
    )

    logger.info(
        "Group journal summary recalculated. summary_id=%s course_id=%s group_id=%s",
        getattr(summary, "id", None),
        course_id,
        group_id,
    )

    return {
        "summary_id": getattr(summary, "id", None),
        "course_id": course_id,
        "group_id": group_id,
    }


@shared_task(name="journal.recalculate_group_student_journal_summaries")
def recalculate_group_student_journal_summaries_task(
    *,
    course_id: int,
    group_id: int,
) -> dict[str, Any]:
    """Пересчитывает индивидуальные сводки студентов по курсу и группе."""

    student_ids = _get_student_ids_for_course_group(
        course_id=course_id,
        group_id=group_id,
    )

    for student_id in student_ids:
        recalculate_journal_summary(
            course_id=course_id,
            group_id=group_id,
            student_id=student_id,
        )

    logger.info(
        "Group student journal summaries recalculated. course_id=%s group_id=%s count=%s",
        course_id,
        group_id,
        len(student_ids),
    )

    return {
        "course_id": course_id,
        "group_id": group_id,
        "students_count": len(student_ids),
    }


@shared_task(name="journal.recalculate_journal_summaries_for_lesson")
def recalculate_journal_summaries_for_lesson_task(
    *,
    lesson_id: int,
) -> dict[str, Any]:
    """Пересчитывает сводки журнала после изменения занятия, посещаемости или оценок."""

    lesson = JournalLesson.objects.only(
        "id",
        "course_id",
        "group_id",
    ).get(id=lesson_id)

    student_ids = set(
        AttendanceRecord.objects.filter(lesson_id=lesson_id).values_list(
            "student_id",
            flat=True,
        )
    ) | set(
        JournalGrade.objects.filter(lesson_id=lesson_id).values_list(
            "student_id",
            flat=True,
        )
    )

    for student_id in student_ids:
        recalculate_journal_summary(
            course_id=lesson.course_id,
            group_id=lesson.group_id,
            student_id=student_id,
        )

    recalculate_journal_summary(
        course_id=lesson.course_id,
        group_id=lesson.group_id,
        student_id=None,
    )

    logger.info(
        "Journal summaries for lesson recalculated. lesson_id=%s students_count=%s",
        lesson_id,
        len(student_ids),
    )

    return {
        "lesson_id": lesson_id,
        "course_id": lesson.course_id,
        "group_id": lesson.group_id,
        "students_count": len(student_ids),
    }


@shared_task(name="journal.sync_topic_progress_for_lesson")
def sync_topic_progress_for_lesson_task(
    *,
    lesson_id: int,
) -> dict[str, Any]:
    """Синхронизирует прогресс тем после изменения занятия журнала."""

    lesson = JournalLesson.objects.select_related("course", "group").get(id=lesson_id)

    progress_items = sync_topic_progress_for_course_group(
        course=lesson.course,
        group=lesson.group,
    )

    logger.info(
        "Topic progress synced for journal lesson. lesson_id=%s course_id=%s "
        "group_id=%s count=%s",
        lesson_id,
        lesson.course_id,
        lesson.group_id,
        len(progress_items),
    )

    return {
        "lesson_id": lesson_id,
        "course_id": lesson.course_id,
        "group_id": lesson.group_id,
        "progress_count": len(progress_items),
    }


@shared_task(name="journal.sync_topic_progress_for_course_group")
def sync_topic_progress_for_course_group_task(
    *,
    course_id: int,
    group_id: int,
) -> dict[str, Any]:
    """Синхронизирует прогресс тем по курсу и группе."""

    lesson = (
        JournalLesson.objects.select_related("course", "group")
        .filter(course_id=course_id, group_id=group_id)
        .order_by("-date", "-id")
        .first()
    )

    if lesson is None:
        logger.info(
            "Topic progress sync skipped: no journal lessons. course_id=%s group_id=%s",
            course_id,
            group_id,
        )

        return {
            "course_id": course_id,
            "group_id": group_id,
            "progress_count": 0,
            "skipped": True,
        }

    progress_items = sync_topic_progress_for_course_group(
        course=lesson.course,
        group=lesson.group,
    )

    logger.info(
        "Topic progress synced for course/group. course_id=%s group_id=%s count=%s",
        course_id,
        group_id,
        len(progress_items),
    )

    return {
        "course_id": course_id,
        "group_id": group_id,
        "progress_count": len(progress_items),
        "skipped": False,
    }
