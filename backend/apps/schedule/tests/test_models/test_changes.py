from __future__ import annotations

from django.test import TestCase

from apps.schedule.constants import ScheduleChangeType
from apps.schedule.tests.factories import (
    create_schedule_change,
    create_scheduled_lesson,
)


class ScheduleChangeModelTestCase(TestCase):
    def test_str_contains_change_type(self):
        change = create_schedule_change(change_type=ScheduleChangeType.CHANGE_TOPIC)

        self.assertIn(change.get_change_type_display(), str(change))

    def test_change_links_to_lesson(self):
        lesson = create_scheduled_lesson()
        change = create_schedule_change(scheduled_lesson=lesson)

        self.assertEqual(change.scheduled_lesson, lesson)
