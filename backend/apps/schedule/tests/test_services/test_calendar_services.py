from __future__ import annotations

from datetime import date

from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.schedule.constants import CalendarType
from apps.schedule.models import ScheduleCalendar
from apps.schedule.services.calendar_services import (
    create_calendar_period,
    mark_holiday,
    mark_practice_period,
    mark_vacation,
    validate_date_is_working_day,
)
from apps.schedule.tests.factories import (
    create_academic_year,
    create_education_period,
    create_organization,
)


class CalendarServicesTestCase(TestCase):
    def test_create_calendar_period_creates_period_and_normalizes_text_fields(self):
        organization = create_organization()
        academic_year = create_academic_year()
        education_period = create_education_period(academic_year=academic_year)

        calendar_period = create_calendar_period(
            organization=organization,
            academic_year=academic_year,
            education_period=education_period,
            name="  Первый семестр  ",
            calendar_type=CalendarType.REGULAR,
            starts_on=date(2025, 9, 1),
            ends_on=date(2025, 12, 31),
            notes="  Основной учебный период  ",
        )

        self.assertIsInstance(calendar_period, ScheduleCalendar)
        self.assertEqual(calendar_period.organization, organization)
        self.assertEqual(calendar_period.academic_year, academic_year)
        self.assertEqual(calendar_period.education_period, education_period)
        self.assertEqual(calendar_period.name, "Первый семестр")
        self.assertEqual(calendar_period.calendar_type, CalendarType.REGULAR)
        self.assertEqual(calendar_period.starts_on, date(2025, 9, 1))
        self.assertEqual(calendar_period.ends_on, date(2025, 12, 31))
        self.assertEqual(calendar_period.notes, "Основной учебный период")
        self.assertTrue(calendar_period.is_active)

    def test_create_calendar_period_runs_model_validation(self):
        organization = create_organization()
        academic_year = create_academic_year()

        with self.assertRaises(ValidationError):
            create_calendar_period(
                organization=organization,
                academic_year=academic_year,
                name="Некорректный период",
                starts_on=date(2025, 12, 31),
                ends_on=date(2025, 9, 1),
            )

    def test_mark_holiday_creates_one_day_holiday_if_ends_on_not_passed(self):
        organization = create_organization()
        academic_year = create_academic_year()

        holiday = mark_holiday(
            organization=organization,
            academic_year=academic_year,
            name="День знаний",
            starts_on=date(2025, 9, 1),
        )

        self.assertEqual(holiday.calendar_type, CalendarType.HOLIDAY)
        self.assertEqual(holiday.starts_on, date(2025, 9, 1))
        self.assertEqual(holiday.ends_on, date(2025, 9, 1))
        self.assertTrue(holiday.is_active)

    def test_mark_holiday_uses_passed_ends_on(self):
        organization = create_organization()
        academic_year = create_academic_year()

        holiday = mark_holiday(
            organization=organization,
            academic_year=academic_year,
            name="Новогодние праздники",
            starts_on=date(2025, 12, 30),
            ends_on=date(2026, 1, 8),
        )

        self.assertEqual(holiday.calendar_type, CalendarType.HOLIDAY)
        self.assertEqual(holiday.starts_on, date(2025, 12, 30))
        self.assertEqual(holiday.ends_on, date(2026, 1, 8))

    def test_mark_vacation_creates_vacation_period(self):
        organization = create_organization()
        academic_year = create_academic_year()

        vacation = mark_vacation(
            organization=organization,
            academic_year=academic_year,
            name="Осенние каникулы",
            starts_on=date(2025, 10, 27),
            ends_on=date(2025, 11, 2),
            notes="Каникулы",
        )

        self.assertEqual(vacation.calendar_type, CalendarType.VACATION)
        self.assertEqual(vacation.starts_on, date(2025, 10, 27))
        self.assertEqual(vacation.ends_on, date(2025, 11, 2))
        self.assertEqual(vacation.notes, "Каникулы")

    def test_mark_practice_period_creates_practice_period(self):
        organization = create_organization()
        academic_year = create_academic_year()

        practice = mark_practice_period(
            organization=organization,
            academic_year=academic_year,
            name="Учебная практика",
            starts_on=date(2026, 3, 1),
            ends_on=date(2026, 3, 14),
        )

        self.assertEqual(practice.calendar_type, CalendarType.PRACTICE)
        self.assertEqual(practice.starts_on, date(2026, 3, 1))
        self.assertEqual(practice.ends_on, date(2026, 3, 14))

    def test_validate_date_is_working_day_allows_regular_day(self):
        organization = create_organization()
        academic_year = create_academic_year()

        create_calendar_period(
            organization=organization,
            academic_year=academic_year,
            name="Обычный период",
            calendar_type=CalendarType.REGULAR,
            starts_on=date(2025, 9, 1),
            ends_on=date(2025, 12, 31),
        )

        validate_date_is_working_day(
            organization=organization,
            academic_year=academic_year,
            target_date=date(2025, 9, 15),
        )

    def test_validate_date_is_working_day_allows_practice_period(self):
        organization = create_organization()
        academic_year = create_academic_year()

        mark_practice_period(
            organization=organization,
            academic_year=academic_year,
            name="Практика",
            starts_on=date(2025, 11, 1),
            ends_on=date(2025, 11, 10),
        )

        validate_date_is_working_day(
            organization=organization,
            academic_year=academic_year,
            target_date=date(2025, 11, 5),
        )

    def test_validate_date_is_working_day_raises_error_for_holiday(self):
        organization = create_organization()
        academic_year = create_academic_year()

        mark_holiday(
            organization=organization,
            academic_year=academic_year,
            name="Праздник",
            starts_on=date(2025, 9, 1),
        )

        with self.assertRaises(ValidationError):
            validate_date_is_working_day(
                organization=organization,
                academic_year=academic_year,
                target_date=date(2025, 9, 1),
            )

    def test_validate_date_is_working_day_raises_error_for_vacation(self):
        organization = create_organization()
        academic_year = create_academic_year()

        mark_vacation(
            organization=organization,
            academic_year=academic_year,
            name="Каникулы",
            starts_on=date(2025, 10, 1),
            ends_on=date(2025, 10, 7),
        )

        with self.assertRaises(ValidationError):
            validate_date_is_working_day(
                organization=organization,
                academic_year=academic_year,
                target_date=date(2025, 10, 3),
            )

    def test_validate_date_is_working_day_ignores_inactive_holiday(self):
        organization = create_organization()
        academic_year = create_academic_year()

        create_calendar_period(
            organization=organization,
            academic_year=academic_year,
            name="Неактивный праздник",
            calendar_type=CalendarType.HOLIDAY,
            starts_on=date(2025, 9, 1),
            ends_on=date(2025, 9, 1),
            is_active=False,
        )

        validate_date_is_working_day(
            organization=organization,
            academic_year=academic_year,
            target_date=date(2025, 9, 1),
        )

    def test_validate_date_is_working_day_ignores_other_organization_periods(self):
        organization = create_organization()
        other_organization = create_organization()
        academic_year = create_academic_year()

        mark_holiday(
            organization=other_organization,
            academic_year=academic_year,
            name="Праздник другой организации",
            starts_on=date(2025, 9, 1),
        )

        validate_date_is_working_day(
            organization=organization,
            academic_year=academic_year,
            target_date=date(2025, 9, 1),
        )
