from __future__ import annotations

from apps.course.models import CourseProgress, LessonProgress
from apps.course.tests.factories.enrollment import create_course_enrollment
from apps.course.tests.factories.structure import create_course_lesson


def create_course_progress(
    *,
    enrollment=None,
    total_lessons_count: int = 0,
    completed_lessons_count: int = 0,
    required_lessons_count: int = 0,
    completed_required_lessons_count: int = 0,
    progress_percent: int = 0,
    spent_minutes: int = 0,
    started_at=None,
    completed_at=None,
    last_activity_at=None,
    last_lesson=None,
):
    """Создаёт или обновляет агрегированный прогресс по курсу."""

    if enrollment is None:
        enrollment = create_course_enrollment()

    progress = CourseProgress.objects.filter(enrollment=enrollment).first()
    if progress is None:
        progress = CourseProgress(enrollment=enrollment)

    progress.total_lessons_count = total_lessons_count
    progress.completed_lessons_count = completed_lessons_count
    progress.required_lessons_count = required_lessons_count
    progress.completed_required_lessons_count = completed_required_lessons_count
    progress.progress_percent = progress_percent
    progress.spent_minutes = spent_minutes
    progress.started_at = started_at
    progress.completed_at = completed_at
    progress.last_activity_at = last_activity_at
    progress.last_lesson = last_lesson
    progress.full_clean()
    progress.save()
    return progress


def create_lesson_progress(
    *,
    enrollment=None,
    lesson=None,
    course_progress=None,
    status: str = LessonProgress.StatusChoices.NOT_STARTED,
    started_at=None,
    completed_at=None,
    last_viewed_at=None,
    spent_minutes: int = 0,
    attempts_count: int = 0,
    score=None,
):
    """Создаёт тестовый прогресс по уроку."""

    if enrollment is None and lesson is None:
        lesson = create_course_lesson()
        enrollment = create_course_enrollment(course=lesson.course)

    if lesson is None:
        lesson = create_course_lesson(course=enrollment.course)

    if enrollment is None:
        enrollment = create_course_enrollment(course=lesson.course)

    if course_progress is None:
        course_progress = CourseProgress.objects.filter(enrollment=enrollment).first()
        if course_progress is None:
            course_progress = create_course_progress(enrollment=enrollment)

    lesson_progress = LessonProgress(
        enrollment=enrollment,
        course_progress=course_progress,
        lesson=lesson,
        status=status,
        started_at=started_at,
        completed_at=completed_at,
        last_viewed_at=last_viewed_at,
        spent_minutes=spent_minutes,
        attempts_count=attempts_count,
        score=score,
    )
    lesson_progress.full_clean()
    lesson_progress.save()
    return lesson_progress
