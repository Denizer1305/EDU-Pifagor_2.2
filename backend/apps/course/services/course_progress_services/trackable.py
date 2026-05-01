from __future__ import annotations


def _get_trackable_lessons_queryset(course):
    """Возвращает опубликованные уроки опубликованных модулей курса."""

    return course.lessons.filter(
        is_published=True,
        module__is_published=True,
    ).order_by("module__order", "order", "id")
