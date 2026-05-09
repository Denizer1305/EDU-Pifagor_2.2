from __future__ import annotations

from apps.course.models import Course, CourseLesson, CourseMaterial, CourseModule


def _get_next_module_order(course: Course) -> int:
    """Возвращает следующий порядковый номер модуля внутри курса."""

    last_module = course.modules.order_by("-order", "-id").first()
    return (last_module.order if last_module else 0) + 1


def _get_next_lesson_order(module: CourseModule) -> int:
    """Возвращает следующий порядковый номер урока внутри модуля."""

    last_lesson = module.lessons.order_by("-order", "-id").first()
    return (last_lesson.order if last_lesson else 0) + 1


def _get_next_material_order(
    course: Course,
    lesson: CourseLesson | None = None,
) -> int:
    """Возвращает следующий порядковый номер материала внутри курса или урока."""

    queryset = CourseMaterial.objects.filter(
        course=course,
        lesson=lesson,
    ).order_by("-order", "-id")
    last_item = queryset.first()

    return (last_item.order if last_item else 0) + 1
