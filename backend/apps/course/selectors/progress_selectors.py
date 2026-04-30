from __future__ import annotations

from apps.course.models import CourseProgress, LessonProgress


def get_course_progress_queryset(
    *,
    course_id: int | None = None,
    student_id: int | None = None,
):
    queryset = CourseProgress.objects.select_related(
        "enrollment",
        "enrollment__course",
        "enrollment__student",
        "last_lesson",
    )

    if course_id:
        queryset = queryset.filter(enrollment__course_id=course_id)

    if student_id:
        queryset = queryset.filter(enrollment__student_id=student_id)

    return queryset.order_by("-updated_at")


def get_course_progress_by_enrollment_id(*, enrollment_id: int):
    return CourseProgress.objects.select_related(
        "enrollment",
        "enrollment__course",
        "enrollment__student",
        "last_lesson",
    ).filter(enrollment_id=enrollment_id).first()


def get_lesson_progress_queryset(
    *,
    enrollment_id: int | None = None,
    course_id: int | None = None,
    lesson_id: int | None = None,
    status: str = "",
):
    queryset = LessonProgress.objects.select_related(
        "enrollment",
        "enrollment__course",
        "enrollment__student",
        "course_progress",
        "lesson",
        "lesson__module",
    )

    if enrollment_id:
        queryset = queryset.filter(enrollment_id=enrollment_id)

    if course_id:
        queryset = queryset.filter(enrollment__course_id=course_id)

    if lesson_id:
        queryset = queryset.filter(lesson_id=lesson_id)

    if status:
        queryset = queryset.filter(status=status)

    return queryset.order_by("lesson__module__order", "lesson__order", "id")
