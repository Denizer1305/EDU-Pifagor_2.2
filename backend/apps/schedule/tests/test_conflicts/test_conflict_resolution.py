from __future__ import annotations

from django.test import TestCase

from apps.schedule.constants import ConflictStatus
from apps.schedule.services.conflict_services import (
    ignore_conflict,
    resolve_conflict,
)
from apps.schedule.tests.factories import (
    create_schedule_conflict,
    create_user,
)


class ConflictResolutionIntegrationTestCase(TestCase):
    def test_resolve_conflict_sets_resolved_status_user_date_and_notes(self):
        user = create_user()
        conflict = create_schedule_conflict(status=ConflictStatus.OPEN)

        resolved_conflict = resolve_conflict(
            conflict,
            user=user,
            notes="Конфликт обработан вручную",
        )

        resolved_conflict.refresh_from_db()

        self.assertEqual(resolved_conflict.status, ConflictStatus.RESOLVED)
        self.assertEqual(resolved_conflict.resolved_by, user)
        self.assertIsNotNone(resolved_conflict.resolved_at)
        self.assertEqual(resolved_conflict.notes, "Конфликт обработан вручную")

    def test_ignore_conflict_sets_ignored_status_user_and_notes(self):
        user = create_user()
        conflict = create_schedule_conflict(status=ConflictStatus.OPEN)

        ignored_conflict = ignore_conflict(
            conflict,
            user=user,
            notes="Конфликт допустим",
        )

        ignored_conflict.refresh_from_db()

        self.assertEqual(ignored_conflict.status, ConflictStatus.IGNORED)
        self.assertEqual(ignored_conflict.resolved_by, user)
        self.assertIsNone(ignored_conflict.resolved_at)
        self.assertEqual(ignored_conflict.notes, "Конфликт допустим")
