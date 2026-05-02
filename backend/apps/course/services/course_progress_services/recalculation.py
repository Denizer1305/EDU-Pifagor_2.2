from __future__ import annotations

from django.db import transaction
from django.utils import timezone

from apps.course.models import (
    CourseEnrollment,
    CourseProgress,
    LessonProgress,
)
from apps.course.services.course_progress_services.ensure import (
    ensure_course_progress,
)
from apps.course.services.course_progress_services.trackable import (
    _get_trackable_lessons_queryset,
)


@transaction.atomic
def recalculate_course_progress(
    *,
    enrollment: CourseEnrollment,
    last_lesson=None,
) -> CourseProgress:
    """Пересчитывает агрегированный прогресс прохождения курса."""

    course = enrollment.course
    course_progress = ensure_course_progress(enrollment=enrollment)

    trackable_lessons = list(_get_trackable_lessons_queryset(course))
    lesson_ids = [lesson.id for lesson in trackable_lessons]

    lesson_progresses = LessonProgress.objects.filter(
        enrollment=enrollment,
        lesson_id__in=lesson_ids,
    )

    completed_ids = set(
        lesson_progresses.filter(
            status=LessonProgress.StatusChoices.COMPLETED,
        ).values_list("lesson_id", flat=True)
    )

    total_lessons_count = len(trackable_lessons)
    completed_lessons_count = len(completed_ids)

    required_lesson_ids = {
        lesson.id for lesson in trackable_lessons if lesson.is_required
    }
    required_lessons_count = len(required_lesson_ids)
    completed_required_lessons_count = len(
        required_lesson_ids.intersection(completed_ids)
    )

    spent_minutes = (
        sum(lesson_progresses.values_list("spent_minutes", flat=True))
        if lesson_ids
        else 0
    )

    progress_percent = 0
    if total_lessons_count > 0:
        progress_percent = round((completed_lessons_count / total_lessons_count) * 100)

    course_progress.total_lessons_count = total_lessons_count
    course_progress.completed_lessons_count = completed_lessons_count
    course_progress.required_lessons_count = required_lessons_count
    course_progress.completed_required_lessons_count = completed_required_lessons_count
    course_progress.progress_percent = min(progress_percent, 100)
    course_progress.spent_minutes = max(0, spent_minutes)
    course_progress.last_activity_at = timezone.now()

    if completed_lessons_count > 0 and course_progress.started_at is None:
        course_progress.started_at = timezone.now()

    if last_lesson is not None:
        course_progress.last_lesson = last_lesson

    is_course_completed = False
    if total_lessons_count > 0:
        if required_lessons_count > 0:
            is_course_completed = (
                completed_required_lessons_count >= required_lessons_count
            )
        else:
            is_course_completed = completed_lessons_count >= total_lessons_count

    if is_course_completed:
        course_progress.progress_percent = 100
        if course_progress.completed_at is None:
            course_progress.completed_at = timezone.now()
    else:
        course_progress.completed_at = None

    course_progress.full_clean()
    course_progress.save()

    enrollment.progress_percent = course_progress.progress_percent
    enrollment.last_activity_at = course_progress.last_activity_at

    if (
        enrollment.status == CourseEnrollment.StatusChoices.ENROLLED
        and completed_lessons_count > 0
    ):
        enrollment.status = CourseEnrollment.StatusChoices.IN_PROGRESS

    if is_course_completed:
        enrollment.status = CourseEnrollment.StatusChoices.COMPLETED
        if enrollment.completed_at is None:
            enrollment.completed_at = timezone.now()
    else:
        if enrollment.status == CourseEnrollment.StatusChoices.COMPLETED:
            enrollment.status = CourseEnrollment.StatusChoices.IN_PROGRESS
        enrollment.completed_at = None

    if enrollment.started_at is None and course_progress.started_at is not None:
        enrollment.started_at = course_progress.started_at

    enrollment.full_clean()
    enrollment.save(
        update_fields=[
            "progress_percent",
            "last_activity_at",
            "status",
            "completed_at",
            "started_at",
            "updated_at",
        ]
    )

    return course_progress
