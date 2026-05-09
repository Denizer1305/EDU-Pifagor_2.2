from __future__ import annotations

from datetime import date, timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from apps.organizations.models import GroupCurator
from apps.organizations.services import (
    assign_group_curator,
    clear_group_join_code,
    disable_group_join_code,
    remove_group_curator,
    set_group_join_code,
)
from apps.organizations.services import (
    create_group as create_group_service,
)
from apps.organizations.tests.factories import (
    create_department,
    create_group,
    create_non_teacher_user,
    create_organization,
    create_teacher_user,
)


class GroupServicesTestCase(TestCase):
    def test_create_group_with_valid_department(self):
        organization = create_organization()
        department = create_department(organization=organization)

        group = create_group_service(
            organization=organization,
            department=department,
            name="ИСП-31",
            code="ISP-31",
        )

        self.assertEqual(group.organization, organization)
        self.assertEqual(group.department, department)

    def test_create_group_with_invalid_department_raises_error(self):
        organization_1 = create_organization(
            name="Организация 1",
            short_name="Орг1",
        )
        organization_2 = create_organization(
            name="Организация 2",
            short_name="Орг2",
        )
        department = create_department(organization=organization_2)

        with self.assertRaises(ValidationError):
            create_group_service(
                organization=organization_1,
                department=department,
                name="ИСП-32",
                code="ISP-32",
            )

    def test_set_disable_and_clear_group_join_code(self):
        group = create_group()

        set_group_join_code(
            group=group,
            raw_code="JOIN-TEST-123",
            expires_at=timezone.now() + timedelta(days=1),
        )
        group.refresh_from_db()
        self.assertTrue(group.has_active_join_code)

        disable_group_join_code(group=group)
        group.refresh_from_db()
        self.assertFalse(group.join_code_is_active)

        clear_group_join_code(group=group)
        group.refresh_from_db()
        self.assertEqual(group.join_code_hash, "")
        self.assertFalse(group.join_code_is_active)
        self.assertIsNone(group.join_code_expires_at)


class GroupCuratorServicesTestCase(TestCase):
    def test_assign_group_curator_for_teacher(self):
        group = create_group()
        teacher = create_teacher_user()

        curator = assign_group_curator(
            group=group,
            teacher=teacher,
            is_primary=True,
            is_active=True,
            starts_at=date.today(),
        )

        self.assertIsInstance(curator, GroupCurator)
        self.assertEqual(curator.group, group)
        self.assertEqual(curator.teacher, teacher)
        self.assertTrue(curator.is_primary)
        self.assertTrue(curator.is_active)

    def test_assign_group_curator_for_non_teacher_raises_error(self):
        group = create_group()
        user = create_non_teacher_user()

        with self.assertRaises(ValidationError):
            assign_group_curator(
                group=group,
                teacher=user,
            )

    def test_remove_group_curator_soft_deactivates_link(self):
        group = create_group()
        teacher = create_teacher_user()

        curator = assign_group_curator(
            group=group,
            teacher=teacher,
            is_primary=True,
        )

        remove_group_curator(
            group=group,
            teacher=teacher,
        )

        curator.refresh_from_db()
        self.assertFalse(curator.is_active)
        self.assertFalse(curator.is_primary)
