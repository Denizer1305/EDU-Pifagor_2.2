from __future__ import annotations

from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from apps.organizations.selectors import (
    get_active_departments_queryset,
    get_active_organization_types_queryset,
    get_active_organizations_queryset,
    get_departments_by_organization_queryset,
    get_departments_queryset,
    get_organization_types_queryset,
    get_organization_with_active_teacher_registration_code,
    get_organizations_queryset,
    get_organizations_with_active_teacher_registration_code_queryset,
)
from apps.organizations.tests.factories import (
    activate_teacher_registration_code,
    create_department,
    create_organization,
    create_organization_type,
)


class OrganizationTypeSelectorsTestCase(TestCase):
    def test_get_organization_types_queryset(self):
        create_organization_type(code="college", name="Колледж")

        queryset = get_organization_types_queryset()

        self.assertEqual(queryset.count(), 1)

    def test_get_active_organization_types_queryset(self):
        create_organization_type(
            code="active",
            name="Активный тип",
            is_active=True,
        )
        create_organization_type(
            code="inactive",
            name="Неактивный тип",
            is_active=False,
        )

        queryset = get_active_organization_types_queryset()

        self.assertEqual(queryset.count(), 1)


class OrganizationSelectorsTestCase(TestCase):
    def test_get_organizations_queryset(self):
        create_organization(
            name="Организация 1",
            short_name="Орг1",
        )

        queryset = get_organizations_queryset()

        self.assertEqual(queryset.count(), 1)

    def test_get_active_organizations_queryset(self):
        create_organization(
            name="Активная организация",
            short_name="Актив",
            is_active=True,
        )
        create_organization(
            name="Неактивная организация",
            short_name="Неакт",
            is_active=False,
        )

        queryset = get_active_organizations_queryset()

        self.assertEqual(queryset.count(), 1)

    def test_get_organizations_with_active_teacher_registration_code_queryset(self):
        organization = create_organization(
            name="С кодом",
            short_name="СК",
        )
        create_organization(
            name="Без кода",
            short_name="БК",
        )
        activate_teacher_registration_code(
            organization,
            raw_code="ORG-CODE-123",
            expires_at=timezone.now() + timedelta(days=1),
        )

        queryset = get_organizations_with_active_teacher_registration_code_queryset()

        self.assertEqual(queryset.count(), 1)
        self.assertIn(organization, queryset)

    def test_get_organization_with_active_teacher_registration_code(self):
        organization = create_organization(
            name="С кодом 2",
            short_name="СК2",
        )
        activate_teacher_registration_code(
            organization,
            raw_code="ORG-CODE-456",
            expires_at=timezone.now() + timedelta(days=1),
        )

        result = get_organization_with_active_teacher_registration_code(
            organization.id,
        )

        self.assertEqual(result.id, organization.id)


class DepartmentSelectorsTestCase(TestCase):
    def test_get_departments_queryset(self):
        create_department()

        queryset = get_departments_queryset()

        self.assertEqual(queryset.count(), 1)

    def test_get_active_departments_queryset(self):
        create_department(
            name="Активное отделение",
            is_active=True,
        )
        create_department(
            name="Неактивное отделение",
            short_name="Н/А",
            is_active=False,
        )

        queryset = get_active_departments_queryset()

        self.assertEqual(queryset.count(), 1)

    def test_get_departments_by_organization_queryset(self):
        organization = create_organization()
        create_department(
            organization=organization,
            name="Отделение 1",
        )
        create_department(
            organization=create_organization(),
            name="Отделение 2",
        )

        queryset = get_departments_by_organization_queryset(organization.id)

        self.assertEqual(queryset.count(), 1)
