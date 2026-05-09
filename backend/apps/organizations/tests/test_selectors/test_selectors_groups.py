from __future__ import annotations

from datetime import date, timedelta

from django.test import TestCase
from django.utils import timezone

from apps.organizations.selectors import (
    get_active_group_curators_queryset,
    get_active_groups_queryset,
    get_group_curators_queryset,
    get_group_with_active_join_code,
    get_groups_by_department_queryset,
    get_groups_by_organization_queryset,
    get_groups_queryset,
    get_groups_with_active_join_code_queryset,
)
from apps.organizations.tests.factories import (
    activate_group_join_code,
    create_department,
    create_group,
    create_group_curator,
    create_organization,
    create_teacher_user,
)


class GroupSelectorsTestCase(TestCase):
    def test_get_groups_queryset(self):
        create_group(
            name="ИСП-51",
            code="ISP-51",
        )

        queryset = get_groups_queryset()

        self.assertEqual(queryset.count(), 1)

    def test_get_active_groups_queryset(self):
        create_group(
            name="ИСП-52",
            code="ISP-52",
            is_active=True,
        )
        create_group(
            name="ИСП-53",
            code="ISP-53",
            is_active=False,
        )

        queryset = get_active_groups_queryset()

        self.assertEqual(queryset.count(), 1)

    def test_get_groups_by_organization_queryset(self):
        organization = create_organization()

        create_group(
            organization=organization,
            name="Группа 1",
            code="G-1",
        )
        create_group(
            organization=create_organization(),
            name="Группа 2",
            code="G-2",
        )

        queryset = get_groups_by_organization_queryset(organization.id)

        self.assertEqual(queryset.count(), 1)

    def test_get_groups_by_department_queryset(self):
        organization = create_organization()
        department = create_department(organization=organization)

        create_group(
            organization=organization,
            department=department,
            name="Группа 1",
            code="GD-1",
        )
        create_group(
            organization=organization,
            department=create_department(organization=organization),
            name="Группа 2",
            code="GD-2",
        )

        queryset = get_groups_by_department_queryset(department.id)

        self.assertEqual(queryset.count(), 1)

    def test_get_groups_with_active_join_code_queryset(self):
        group = create_group(
            name="ИСП-54",
            code="ISP-54",
        )
        create_group(
            name="ИСП-55",
            code="ISP-55",
        )
        activate_group_join_code(
            group,
            raw_code="JOIN-123456",
            expires_at=timezone.now() + timedelta(days=1),
        )

        queryset = get_groups_with_active_join_code_queryset()

        self.assertEqual(queryset.count(), 1)
        self.assertIn(group, queryset)

    def test_get_group_with_active_join_code(self):
        group = create_group(
            name="ИСП-56",
            code="ISP-56",
        )
        activate_group_join_code(
            group,
            raw_code="JOIN-654321",
            expires_at=timezone.now() + timedelta(days=1),
        )

        result = get_group_with_active_join_code(group.id)

        self.assertEqual(result.id, group.id)


class GroupCuratorSelectorsTestCase(TestCase):
    def test_get_group_curators_queryset(self):
        group = create_group()
        teacher = create_teacher_user()
        create_group_curator(
            group=group,
            teacher=teacher,
        )

        queryset = get_group_curators_queryset()

        self.assertEqual(queryset.count(), 1)

    def test_get_active_group_curators_queryset(self):
        group = create_group()
        active_curator = create_group_curator(
            group=group,
            teacher=create_teacher_user(email="active_curator@example.com"),
            is_active=True,
            starts_at=date.today() - timedelta(days=1),
            ends_at=date.today() + timedelta(days=1),
        )
        create_group_curator(
            group=group,
            teacher=create_teacher_user(email="inactive_curator@example.com"),
            is_active=False,
            starts_at=date.today() - timedelta(days=10),
            ends_at=date.today() - timedelta(days=1),
        )

        queryset = get_active_group_curators_queryset(group_id=group.id)

        self.assertEqual(queryset.count(), 1)
        self.assertIn(active_curator, queryset)
