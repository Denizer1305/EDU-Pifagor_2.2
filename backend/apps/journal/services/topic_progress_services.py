from __future__ import annotations

import logging
from datetime import date, datetime

from django.db import transaction
from django.utils import timezone

from apps.course.models import CourseLesson
from apps.journal.models import JournalLesson, TopicProgress
from apps.journal.models.choices import JournalLessonStatus, TopicProgressStatus

logger = logging.getLogger(__name__)


@transaction.atomic
def sync_topic_progress_for_course_group(
    *,
    course,
    group,
) -> list[TopicProgress]:
    """Синхронизирует прогресс тем по курсу и группе.

    Не создаёт новых таблиц.
    Создаёт/обновляет строки TopicProgress для существующих CourseLesson.
    """

    logger.info(
        "sync_topic_progress_for_course_group started course_id=%s group_id=%s",
        getattr(course, "id", None),
        getattr(group, "id", None),
    )

    course_lessons = CourseLesson.objects.filter(course=course).order_by("order", "id")

    progress_items: list[TopicProgress] = []

    for course_lesson in course_lessons:
        journal_lesson = _get_latest_conducted_journal_lesson(
            course=course,
            group=group,
            course_lesson=course_lesson,
        )

        planned_date = _normalize_date(getattr(course_lesson, "available_from", None))

        status, actual_date, days_behind = _calculate_topic_status(
            planned_date=planned_date,
            journal_lesson=journal_lesson,
        )

        progress, _ = TopicProgress.objects.update_or_create(
            course=course,
            group=group,
            lesson=course_lesson,
            defaults={
                "journal_lesson": journal_lesson,
                "planned_date": planned_date,
                "actual_date": actual_date,
                "status": status,
                "days_behind": days_behind,
            },
        )

        progress_items.append(progress)

    logger.info(
        "sync_topic_progress_for_course_group completed course_id=%s group_id=%s count=%s",
        getattr(course, "id", None),
        getattr(group, "id", None),
        len(progress_items),
    )

    return progress_items


def _get_latest_conducted_journal_lesson(
    *,
    course,
    group,
    course_lesson: CourseLesson,
) -> JournalLesson | None:
    return (
        JournalLesson.objects.filter(
            course=course,
            group=group,
            course_lesson=course_lesson,
            status=JournalLessonStatus.CONDUCTED,
        )
        .order_by("-date", "-id")
        .first()
    )


def _calculate_topic_status(
    *,
    planned_date: date | None,
    journal_lesson: JournalLesson | None,
) -> tuple[str, date | None, int]:
    if journal_lesson is not None:
        return TopicProgressStatus.COMPLETED, journal_lesson.date, 0

    if planned_date is None:
        return TopicProgressStatus.PLANNED, None, 0

    today = timezone.localdate()

    if planned_date < today:
        return TopicProgressStatus.BEHIND, None, (today - planned_date).days

    return TopicProgressStatus.PLANNED, None, 0


def _normalize_date(value) -> date | None:
    if value is None:
        return None

    if isinstance(value, datetime):
        if timezone.is_aware(value):
            return timezone.localdate(value)

        return value.date()

    if isinstance(value, date):
        return value

    if hasattr(value, "date"):
        normalized = value.date()
        if isinstance(normalized, datetime):
            return (
                timezone.localdate(normalized)
                if timezone.is_aware(normalized)
                else normalized.date()
            )

        return normalized

    return None
