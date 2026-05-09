from __future__ import annotations

from django.test import TestCase

from apps.schedule.constants import ConflictSeverity, ConflictStatus, ConflictType
from apps.schedule.tests.factories import create_schedule_conflict


class ScheduleConflictModelTestCase(TestCase):
    def test_str_contains_conflict_type(self):
        conflict = create_schedule_conflict(
            conflict_type=ConflictType.TEACHER_OVERLAP,
        )

        self.assertIn(str(conflict.get_conflict_type_display()), str(conflict))

    def test_conflict_fields_are_saved(self):
        conflict = create_schedule_conflict(
            conflict_type=ConflictType.ROOM_OVERLAP,
            severity=ConflictSeverity.WARNING,
            status=ConflictStatus.OPEN,
        )

        self.assertEqual(conflict.conflict_type, ConflictType.ROOM_OVERLAP)
        self.assertEqual(conflict.severity, ConflictSeverity.WARNING)
        self.assertEqual(conflict.status, ConflictStatus.OPEN)
