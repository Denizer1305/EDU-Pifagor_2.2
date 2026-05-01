from __future__ import annotations

from django.test import TestCase

from apps.course.models import CourseEnrollment, LessonProgress
from apps.course.services import (
    mark_lesson_completed,
    mark_lesson_in_progress,
    recalculate_course_progress,
    start_course_enrollment,
)
from apps.course.tests.factories import (
    create_course_enrollment as create_course_enrollment_factory,
    create_course_lesson as create_course_lesson_factory,
)


class CourseProgressServicesTestCase(TestCase):
    def test_start_course_enrollment(self):
        enrollment = create_course_enrollment_factory()

        updated = start_course_enrollment(enrollment=enrollment)

        self.assertEqual(updated.status, CourseEnrollment.StatusChoices.IN_PROGRESS)
        self.assertIsNotNone(updated.started_at)

    def test_mark_lesson_in_progress(self):
        lesson = create_course_lesson_factory()
        enrollment = create_course_enrollment_factory(course=lesson.course)

        lesson_progress = mark_lesson_in_progress(
            enrollment=enrollment,
            lesson=lesson,
        )

        self.assertEqual(
            lesson_progress.status,
            LessonProgress.StatusChoices.IN_PROGRESS,
        )

    def test_mark_lesson_completed_and_recalculate_progress(self):
        lesson = create_course_lesson_factory()
        enrollment = create_course_enrollment_factory(course=lesson.course)

        lesson_progress = mark_lesson_completed(
            enrollment=enrollment,
            lesson=lesson,
            spent_minutes=15,
            attempts_increment=True,
        )

        self.assertEqual(
            lesson_progress.status,
            LessonProgress.StatusChoices.COMPLETED,
        )

        progress = recalculate_course_progress(enrollment=enrollment)
        self.assertEqual(progress.progress_percent, 100)

        enrollment.refresh_from_db()
        self.assertEqual(enrollment.status, CourseEnrollment.StatusChoices.COMPLETED)
