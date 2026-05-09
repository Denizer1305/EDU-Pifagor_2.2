from __future__ import annotations

from datetime import date

from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.schedule.constants import CalendarType, WeekType
from apps.schedule.tests.factories import (
    create_schedule_calendar,
    create_schedule_week_template,
)


class ScheduleCalendarModelTestCase(TestCase):
    def test_str_contains_name(self):
        calendar = create_schedule_calendar(name="Осенние каникулы")

        self.assertIn("Осенние каникулы", str(calendar))

    def test_ends_on_must_not_be_before_starts_on(self):
        calendar = create_schedule_calendar(
            starts_on=date(2025, 9, 10),
            ends_on=date(2025, 9, 10),
        )
        calendar.ends_on = date(2025, 9, 1)

        with self.assertRaises(ValidationError):
            calendar.full_clean()

    def test_calendar_type_is_saved(self):
        calendar = create_schedule_calendar(calendar_type=CalendarType.HOLIDAY)

        self.assertEqual(calendar.calendar_type, CalendarType.HOLIDAY)


class ScheduleWeekTemplateModelTestCase(TestCase):
    def test_str_contains_name(self):
        template = create_schedule_week_template(name="Числитель")

        self.assertIn("Числитель", str(template))

    def test_ends_on_must_not_be_before_starts_on(self):
        template = create_schedule_week_template(
            starts_on=date(2025, 9, 1),
            ends_on=date(2025, 9, 7),
        )
        template.ends_on = date(2025, 8, 31)

        with self.assertRaises(ValidationError):
            template.full_clean()

    def test_week_type_is_saved(self):
        template = create_schedule_week_template(week_type=WeekType.NUMERATOR)

        self.assertEqual(template.week_type, WeekType.NUMERATOR)
