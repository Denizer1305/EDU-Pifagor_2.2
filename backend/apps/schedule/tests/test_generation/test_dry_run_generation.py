from __future__ import annotations

from datetime import date

from django.test import TestCase

from apps.schedule.constants import Weekday
from apps.schedule.models import ScheduledLesson
from apps.schedule.services.generation_services import dry_run_generation
from apps.schedule.tests.factories import create_schedule_pattern

from . import COMPLETED_STATUS, create_schedule_generation_batch


class DryRunGenerationTestCase(TestCase):
    def test_dry_run_generation_counts_lessons_but_does_not_create_them(self):
        pattern = create_schedule_pattern(
            weekday=Weekday.MONDAY,
            starts_on=date(2025, 9, 1),
            ends_on=date(2025, 9, 8),
            is_active=True,
        )
        batch = create_schedule_generation_batch(
            pattern=pattern,
            dry_run=False,
        )

        result = dry_run_generation(
            batch=batch,
            starts_on=date(2025, 9, 1),
            ends_on=date(2025, 9, 8),
        )

        result.refresh_from_db()

        self.assertTrue(result.dry_run)
        self.assertEqual(result.status, COMPLETED_STATUS)
        self.assertEqual(result.lessons_created, 2)
        self.assertEqual(result.lessons_updated, 0)
        self.assertFalse(ScheduledLesson.objects.filter(pattern=pattern).exists())
