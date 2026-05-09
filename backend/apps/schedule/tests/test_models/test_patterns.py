from __future__ import annotations

from datetime import date

from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.schedule.constants import ScheduleStatus, Weekday
from apps.schedule.tests.factories import (
    create_course,
    create_course_lesson,
    create_schedule_pattern,
    create_schedule_pattern_audience,
)


class SchedulePatternModelTestCase(TestCase):
    def test_str_contains_title_weekday_and_time(self):
        pattern = create_schedule_pattern(
            title="Тестовый шаблон расписания",
            weekday=Weekday.MONDAY,
        )

        pattern_str = str(pattern)

        self.assertIn("Тестовый шаблон расписания", pattern_str)
        self.assertIn("Понедельник", pattern_str)
        self.assertIn("09:00", pattern_str)
        self.assertIn("10:30", pattern_str)

    def test_ends_on_must_not_be_before_starts_on(self):
        pattern = create_schedule_pattern(
            starts_on=date(2025, 9, 1),
            ends_on=date(2025, 9, 30),
        )
        pattern.ends_on = date(2025, 8, 31)

        with self.assertRaises(ValidationError):
            pattern.full_clean()

    def test_course_lesson_must_belong_to_course(self):
        first_course = create_course()
        second_course = create_course()
        foreign_lesson = create_course_lesson(course=second_course)

        pattern = create_schedule_pattern(
            course=first_course,
            course_lesson=foreign_lesson,
        )

        with self.assertRaises(ValidationError):
            pattern.full_clean()

    def test_status_is_saved(self):
        pattern = create_schedule_pattern(status=ScheduleStatus.PUBLISHED)

        self.assertEqual(pattern.status, ScheduleStatus.PUBLISHED)


class SchedulePatternAudienceModelTestCase(TestCase):
    def test_pattern_audience_links_group_to_pattern(self):
        audience = create_schedule_pattern_audience()

        self.assertIsNotNone(audience.pattern)
        self.assertIsNotNone(audience.group)
        self.assertEqual(
            audience.pattern.organization_id,
            audience.group.organization_id,
        )
