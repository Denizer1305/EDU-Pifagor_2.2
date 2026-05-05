from __future__ import annotations

from datetime import date, time
from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.schedule.constants import ScheduleStatus
from apps.schedule.tests.factories import (
    create_course,
    create_course_lesson,
    create_scheduled_lesson,
    create_scheduled_lesson_audience,
)


class ScheduledLessonModelTestCase(TestCase):
    def test_str_contains_course_and_date(self):
        lesson = create_scheduled_lesson(
            lesson_date=date(2025, 9, 1),
            title="Тестовое занятие",
        )

        lesson_str = str(lesson)

        self.assertIn("2025-09-01", lesson_str)
        self.assertIn("Тестовое занятие", lesson_str)

    def test_ends_at_must_be_after_starts_at(self):
        lesson = create_scheduled_lesson()
        lesson.starts_at = time(10, 0)
        lesson.ends_at = time(9, 0)

        with self.assertRaises(ValidationError):
            lesson.full_clean()

    def test_course_lesson_must_belong_to_course(self):
        first_course = create_course()
        second_course = create_course()
        foreign_lesson = create_course_lesson(course=second_course)

        lesson = create_scheduled_lesson(
            course=first_course,
            course_lesson=foreign_lesson,
        )

        with self.assertRaises(ValidationError):
            lesson.full_clean()

    def test_status_is_saved(self):
        with patch("apps.schedule.signals.create_journal_lesson_from_schedule"):
            lesson = create_scheduled_lesson(status=ScheduleStatus.PUBLISHED)

        self.assertEqual(lesson.status, ScheduleStatus.PUBLISHED)

    def test_locked_flag_is_saved(self):
        lesson = create_scheduled_lesson(is_locked=True)

        self.assertTrue(lesson.is_locked)


class ScheduledLessonAudienceModelTestCase(TestCase):
    def test_lesson_audience_links_group_to_lesson(self):
        audience = create_scheduled_lesson_audience()

        self.assertEqual(
            audience.scheduled_lesson.organization_id,
            audience.group.organization_id,
        )
