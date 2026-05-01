from __future__ import annotations

from apps.course.models import Course, CourseModule


def _recalculate_module_estimated_minutes(module: CourseModule) -> CourseModule:
    """Пересчитывает длительность модуля по урокам."""

    minutes_values = module.lessons.values_list("estimated_minutes", flat=True)
    total_minutes = sum(minutes_values) if minutes_values else 0

    if module.estimated_minutes != total_minutes:
        module.estimated_minutes = total_minutes
        module.full_clean()
        module.save(update_fields=["estimated_minutes", "updated_at"])

    return module


def _recalculate_course_estimated_minutes(course: Course) -> Course:
    """Пересчитывает длительность курса по опубликованным урокам."""

    minutes_values = course.lessons.filter(
        is_published=True,
        module__is_published=True,
    ).values_list("estimated_minutes", flat=True)
    total_minutes = sum(minutes_values) if minutes_values else 0

    if course.estimated_minutes != total_minutes:
        course.estimated_minutes = total_minutes
        course.full_clean()
        course.save(update_fields=["estimated_minutes", "updated_at"])

    return course
