from __future__ import annotations

from apps.course.models import Course


def _get_course_from_obj(obj):
    """Извлекает курс из объекта домена course."""

    if obj is None:
        return None

    if isinstance(obj, Course):
        return obj

    course = getattr(obj, "course", None)
    if course is not None:
        return course

    module = getattr(obj, "module", None)
    if module is not None and getattr(module, "course", None) is not None:
        return module.course

    lesson = getattr(obj, "lesson", None)
    if lesson is not None and getattr(lesson, "course", None) is not None:
        return lesson.course

    enrollment = getattr(obj, "enrollment", None)
    if enrollment is not None and getattr(enrollment, "course", None) is not None:
        return enrollment.course

    course_progress = getattr(obj, "course_progress", None)
    if course_progress is not None:
        enrollment = getattr(course_progress, "enrollment", None)
        if enrollment is not None and getattr(enrollment, "course", None) is not None:
            return enrollment.course

    assignment = getattr(obj, "assignment", None)
    if assignment is not None and getattr(assignment, "course", None) is not None:
        return assignment.course

    return None


def _get_student_from_obj(obj):
    """Извлекает студента из объекта домена course."""

    if obj is None:
        return None

    student = getattr(obj, "student", None)
    if student is not None:
        return student

    enrollment = getattr(obj, "enrollment", None)
    if enrollment is not None and getattr(enrollment, "student", None) is not None:
        return enrollment.student

    course_progress = getattr(obj, "course_progress", None)
    if course_progress is not None:
        enrollment = getattr(course_progress, "enrollment", None)
        if enrollment is not None and getattr(enrollment, "student", None) is not None:
            return enrollment.student

    return None
