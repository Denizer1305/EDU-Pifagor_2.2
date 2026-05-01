from __future__ import annotations

from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from apps.organizations.services import (
    clear_teacher_registration_code,
    disable_teacher_registration_code,
    set_teacher_registration_code,
)
from apps.organizations.tests.factories import create_organization


class OrganizationServicesTestCase(TestCase):
    def test_set_disable_and_clear_teacher_registration_code(self):
        organization = create_organization()

        set_teacher_registration_code(
            organization=organization,
            raw_code="TEACHER-TEST-123",
            expires_at=timezone.now() + timedelta(days=1),
        )
        organization.refresh_from_db()
        self.assertTrue(organization.has_active_teacher_registration_code)

        disable_teacher_registration_code(organization=organization)
        organization.refresh_from_db()
        self.assertFalse(organization.teacher_registration_code_is_active)

        clear_teacher_registration_code(organization=organization)
        organization.refresh_from_db()
        self.assertEqual(organization.teacher_registration_code_hash, "")
        self.assertFalse(organization.teacher_registration_code_is_active)
        self.assertIsNone(organization.teacher_registration_code_expires_at)
