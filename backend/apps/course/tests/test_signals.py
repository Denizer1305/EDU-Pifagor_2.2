from __future__ import annotations

from django.test import TestCase

from apps.course.models import CourseProgress
from apps.course.tests.factories import (
    create_course,
    create_course_enrollment,
    create_course_lesson,
    create_course_module,
    create_lesson_progress,
)


class CourseSignalsTestCase(TestCase):
    def test_course_enrollment_creates_progress_via_signal(self):
        enrollment = create_course_enrollment()

        self.assertTrue(
            CourseProgress.objects.filter(enrollment=enrollment).exists()
        )

    def test_lesson_save_recalculates_module_and_course_minutes(self):
        course = create_course()
        module = create_course_module(course=course, estimated_minutes=0)

        create_course_lesson(
            course=course,
            module=module,
            estimated_minutes=30,
            is_published=True,
        )
        module.refresh_from_db()
        course.refresh_from_db()

        self.assertEqual(module.estimated_minutes, 30)
        self.assertEqual(course.estimated_minutes, 30)

    def test_lesson_delete_recalculates_minutes(self):
        course = create_course()
        module = create_course_module(course=course)

        lesson = create_course_lesson(
            course=course,
            module=module,
            estimated_minutes=25,
        )

        lesson.delete()
        module.refresh_from_db()
        course.refresh_from_db()

        self.assertEqual(module.estimated_minutes, 0)
        self.assertEqual(course.estimated_minutes, 0)

    def test_lesson_progress_signal_recalculates_course_progress(self):
        lesson = create_course_lesson(estimated_minutes=10)
        enrollment = create_course_enrollment(course=lesson.course)

        create_lesson_progress(
            enrollment=enrollment,
            lesson=lesson,
            status="completed",
            spent_minutes=10,
        )

        progress = CourseProgress.objects.get(enrollment=enrollment)
        self.assertGreaterEqual(progress.completed_lessons_count, 1)
