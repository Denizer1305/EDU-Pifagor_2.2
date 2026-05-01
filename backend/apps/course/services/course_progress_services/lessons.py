from __future__ import annotations

from django.db import transaction
from django.utils import timezone

from apps.course.models import CourseEnrollment, LessonProgress
from apps.course.services.course_progress_services.enrollment import (
    start_course_enrollment,
)
from apps.course.services.course_progress_services.ensure import (
    ensure_lesson_progress,
)
from apps.course.services.course_progress_services.recalculation import (
    recalculate_course_progress,
)


@transaction.atomic
def mark_lesson_in_progress(
    *,
    enrollment: CourseEnrollment,
    lesson,
) -> LessonProgress:
    """Отмечает урок как начатый студентом."""

    start_course_enrollment(enrollment=enrollment)
    lesson_progress = ensure_lesson_progress(
        enrollment=enrollment,
        lesson=lesson,
    )

    if lesson_progress.status == LessonProgress.StatusChoices.NOT_STARTED:
        lesson_progress.status = LessonProgress.StatusChoices.IN_PROGRESS

    if lesson_progress.started_at is None:
        lesson_progress.started_at = timezone.now()

    lesson_progress.last_viewed_at = timezone.now()
    lesson_progress.full_clean()
    lesson_progress.save(
        update_fields=[
            "status",
            "started_at",
            "last_viewed_at",
            "updated_at",
        ]
    )

    recalculate_course_progress(enrollment=enrollment, last_lesson=lesson)
    return lesson_progress


@transaction.atomic
def mark_lesson_completed(
    *,
    enrollment: CourseEnrollment,
    lesson,
    spent_minutes: int | None = None,
    score=None,
    attempts_increment: bool = True,
) -> LessonProgress:
    """Отмечает урок как завершённый и пересчитывает прогресс курса."""

    start_course_enrollment(enrollment=enrollment)
    lesson_progress = ensure_lesson_progress(
        enrollment=enrollment,
        lesson=lesson,
    )

    lesson_progress.status = LessonProgress.StatusChoices.COMPLETED

    if lesson_progress.started_at is None:
        lesson_progress.started_at = timezone.now()

    if lesson_progress.completed_at is None:
        lesson_progress.completed_at = timezone.now()

    lesson_progress.last_viewed_at = timezone.now()

    if spent_minutes is not None:
        lesson_progress.spent_minutes = max(0, spent_minutes)

    if score is not None:
        lesson_progress.score = score

    if attempts_increment:
        lesson_progress.attempts_count += 1

    lesson_progress.full_clean()
    lesson_progress.save(
        update_fields=[
            "status",
            "started_at",
            "completed_at",
            "last_viewed_at",
            "spent_minutes",
            "score",
            "attempts_count",
            "updated_at",
        ]
    )

    recalculate_course_progress(enrollment=enrollment, last_lesson=lesson)
    return lesson_progress
