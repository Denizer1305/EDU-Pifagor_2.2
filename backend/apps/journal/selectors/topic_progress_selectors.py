from __future__ import annotations

from typing import Any

from django.db.models import QuerySet
from django.shortcuts import get_object_or_404

from apps.journal.models import TopicProgress
from apps.journal.models.choices import TopicProgressStatus


def get_topic_progress_queryset(
    *,
    course: Any | None = None,
    group: Any | None = None,
    lesson: Any | None = None,
    status: str | None = None,
    only_behind: bool = False,
) -> QuerySet[TopicProgress]:
    """Возвращает queryset прогресса тем с фильтрами."""

    queryset = (
        TopicProgress.objects.select_related(
            "course",
            "group",
            "lesson",
            "journal_lesson",
        )
        .all()
        .order_by("planned_date", "lesson_id", "id")
    )

    if course is not None:
        queryset = queryset.filter(course=course)

    if group is not None:
        queryset = queryset.filter(group=group)

    if lesson is not None:
        queryset = queryset.filter(lesson=lesson)

    if status:
        queryset = queryset.filter(status=status)

    if only_behind:
        queryset = queryset.filter(days_behind__gt=0)

    return queryset


def get_topic_progress_by_id(progress_id: int) -> TopicProgress:
    """Возвращает прогресс темы по id или 404."""

    return get_object_or_404(
        get_topic_progress_queryset(),
        id=progress_id,
    )


def get_topic_progress_for_course_group(
    *,
    course: Any,
    group: Any,
) -> QuerySet[TopicProgress]:
    """Возвращает прогресс тем по курсу и группе."""

    return get_topic_progress_queryset(
        course=course,
        group=group,
    )


def get_topic_progress_for_lesson(
    *,
    course: Any,
    group: Any,
    lesson: Any,
) -> TopicProgress | None:
    """Возвращает прогресс конкретной темы."""

    return get_topic_progress_queryset(
        course=course,
        group=group,
        lesson=lesson,
    ).first()


def get_behind_topics(
    *,
    course: Any | None = None,
    group: Any | None = None,
) -> QuerySet[TopicProgress]:
    """Возвращает темы с отставанием."""

    return get_topic_progress_queryset(
        course=course,
        group=group,
        only_behind=True,
    )


def get_completed_topics(
    *,
    course: Any | None = None,
    group: Any | None = None,
) -> QuerySet[TopicProgress]:
    """Возвращает завершённые темы."""

    return get_topic_progress_queryset(
        course=course,
        group=group,
        status=TopicProgressStatus.COMPLETED,
    )


def get_planned_topics(
    *,
    course: Any | None = None,
    group: Any | None = None,
) -> QuerySet[TopicProgress]:
    """Возвращает запланированные темы."""

    return get_topic_progress_queryset(
        course=course,
        group=group,
        status=TopicProgressStatus.PLANNED,
    )


def get_in_progress_topics(
    *,
    course: Any | None = None,
    group: Any | None = None,
) -> QuerySet[TopicProgress]:
    """Возвращает темы в процессе прохождения."""

    return get_topic_progress_queryset(
        course=course,
        group=group,
        status=TopicProgressStatus.IN_PROGRESS,
    )


def get_skipped_topics(
    *,
    course: Any | None = None,
    group: Any | None = None,
) -> QuerySet[TopicProgress]:
    """Возвращает пропущенные темы."""

    return get_topic_progress_queryset(
        course=course,
        group=group,
        status=TopicProgressStatus.SKIPPED,
    )
