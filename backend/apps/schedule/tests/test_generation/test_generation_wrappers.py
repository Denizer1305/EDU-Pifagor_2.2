from __future__ import annotations

from datetime import date

from django.test import TestCase

from apps.schedule.constants import GenerationSource, Weekday
from apps.schedule.services.generation_services import (
    generate_lessons_from_course,
    generate_lessons_from_ktp,
)
from apps.schedule.tests.factories import create_schedule_pattern

from . import COMPLETED_STATUS, create_schedule_generation_batch


class GenerationSourceWrappersTestCase(TestCase):
    def test_generate_lessons_from_ktp_sets_batch_source(self):
        pattern = create_schedule_pattern(
            weekday=Weekday.MONDAY,
            starts_on=date(2025, 9, 1),
            ends_on=date(2025, 9, 1),
            is_active=True,
        )
        batch = create_schedule_generation_batch(
            pattern=pattern,
            dry_run=True,
        )

        result = generate_lessons_from_ktp(
            batch=batch,
            starts_on=date(2025, 9, 1),
            ends_on=date(2025, 9, 1),
            detect_conflicts=False,
        )

        result.refresh_from_db()

        self.assertEqual(result.source, GenerationSource.KTP)
        self.assertEqual(result.status, COMPLETED_STATUS)

    def test_generate_lessons_from_course_sets_batch_source(self):
        pattern = create_schedule_pattern(
            weekday=Weekday.MONDAY,
            starts_on=date(2025, 9, 1),
            ends_on=date(2025, 9, 1),
            is_active=True,
        )
        batch = create_schedule_generation_batch(
            pattern=pattern,
            dry_run=True,
        )

        result = generate_lessons_from_course(
            batch=batch,
            starts_on=date(2025, 9, 1),
            ends_on=date(2025, 9, 1),
            detect_conflicts=False,
        )

        result.refresh_from_db()

        self.assertEqual(result.source, GenerationSource.COURSE)
        self.assertEqual(result.status, COMPLETED_STATUS)
