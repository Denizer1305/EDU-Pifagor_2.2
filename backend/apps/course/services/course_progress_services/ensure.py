from __future__ import annotations

from django.db import transaction

from apps.course.models import (
    CourseEnrollment,
    CourseProgress,
    LessonProgress,
)


@transaction.atomic
def ensure_course_progress(*, enrollment: CourseEnrollment) -> CourseProgress:
    """Гарантирует наличие агрегированного прогресса по курсу."""

    progress, _ = CourseProgress.objects.get_or_create(
        enrollment=enrollment,
    )
    return progress


@transaction.atomic
def ensure_lesson_progress(
    *,
    enrollment: CourseEnrollment,
    lesson,
) -> LessonProgress:
    """Гарантирует наличие прогресса по конкретному уроку."""

    course_progress = ensure_course_progress(enrollment=enrollment)

    lesson_progress, _ = LessonProgress.objects.get_or_create(
        enrollment=enrollment,
        lesson=lesson,
        defaults={
            "course_progress": course_progress,
        },
    )

    if lesson_progress.course_progress_id != course_progress.id:
        lesson_progress.course_progress = course_progress
        lesson_progress.full_clean()
        lesson_progress.save(update_fields=["course_progress", "updated_at"])

    return lesson_progress
