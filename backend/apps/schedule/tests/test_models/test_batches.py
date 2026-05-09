from __future__ import annotations

from django.test import TestCase

from apps.schedule.constants import BatchStatus, GenerationSource, ImportSourceType
from apps.schedule.tests.factories import (
    create_schedule_generation_batch,
    create_schedule_import_batch,
)


class ScheduleGenerationBatchModelTestCase(TestCase):
    def test_str_contains_name(self):
        batch = create_schedule_generation_batch(name="Генерация 1 семестра")

        self.assertIn("Генерация 1 семестра", str(batch))

    def test_defaults_are_saved(self):
        batch = create_schedule_generation_batch(
            source=GenerationSource.PATTERNS,
            status=BatchStatus.PENDING,
            dry_run=True,
        )

        self.assertEqual(batch.source, GenerationSource.PATTERNS)
        self.assertEqual(batch.status, BatchStatus.PENDING)
        self.assertTrue(batch.dry_run)


class ScheduleImportBatchModelTestCase(TestCase):
    def test_str_contains_source_type_display(self):
        batch = create_schedule_import_batch(source_type=ImportSourceType.MANUAL)

        self.assertIn(str(batch.get_source_type_display()), str(batch))

    def test_defaults_are_saved(self):
        batch = create_schedule_import_batch(
            source_type=ImportSourceType.MANUAL,
            status=BatchStatus.PENDING,
        )

        self.assertEqual(batch.source_type, ImportSourceType.MANUAL)
        self.assertEqual(batch.status, BatchStatus.PENDING)
