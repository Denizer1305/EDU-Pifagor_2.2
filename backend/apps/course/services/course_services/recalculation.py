from __future__ import annotations

from apps.course.models import Course


def _recalculate_course_estimated_minutes(course: Course) -> Course:
    """Пересчитывает плановую длительность курса по опубликованным урокам."""

    estimated_minutes = course.lessons.filter(
        is_published=True,
        module__is_published=True,
    ).values_list("estimated_minutes", flat=True)
    total_minutes = sum(estimated_minutes) if estimated_minutes else 0

    if course.estimated_minutes != total_minutes:
        course.estimated_minutes = total_minutes
        course.full_clean()
        course.save(update_fields=["estimated_minutes", "updated_at"])

    return course
