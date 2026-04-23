from __future__ import annotations

from datetime import date, timedelta

from django.test import TestCase
from django.utils import timezone

from apps.organizations.selectors import (
    get_active_departments_queryset,
    get_active_group_curators_queryset,
    get_active_groups_queryset,
    get_active_organization_types_queryset,
    get_active_organizations_queryset,
    get_active_subject_categories_queryset,
    get_active_subjects_queryset,
    get_active_teacher_organizations_queryset,
    get_departments_by_organization_queryset,
    get_departments_queryset,
    get_group_curators_queryset,
    get_group_with_active_join_code,
    get_groups_by_department_queryset,
    get_groups_by_organization_queryset,
    get_groups_queryset,
    get_groups_with_active_join_code_queryset,
    get_organization_types_queryset,
    get_organization_with_active_teacher_registration_code,
    get_organizations_queryset,
    get_organizations_with_active_teacher_registration_code_queryset,
    get_subject_categories_queryset,
    get_subjects_queryset,
    get_teacher_organizations_queryset,
    get_teacher_subjects_queryset,
)
from apps.organizations.tests.factories import (
    activate_group_join_code,
    activate_teacher_registration_code,
    create_department,
    create_group,
    create_group_curator,
    create_organization,
    create_organization_type,
    create_subject,
    create_subject_category,
    create_teacher_organization,
    create_teacher_subject,
    create_teacher_user,
)


class OrganizationSelectorsTestCase(TestCase):
    def test_get_organization_types_queryset(self):
        create_organization_type(code="college", name="Колледж")
        queryset = get_organization_types_queryset()

        self.assertEqual(queryset.count(), 1)

    def test_get_active_organization_types_queryset(self):
        create_organization_type(code="active", name="Активный тип", is_active=True)
        create_organization_type(code="inactive", name="Неактивный тип", is_active=False)

        queryset = get_active_organization_types_queryset()
        self.assertEqual(queryset.count(), 1)

    def test_get_organizations_queryset(self):
        create_organization(name="Организация 1", short_name="Орг1")
        queryset = get_organizations_queryset()

        self.assertEqual(queryset.count(), 1)

    def test_get_active_organizations_queryset(self):
        create_organization(name="Активная организация", short_name="Актив", is_active=True)
        create_organization(name="Неактивная организация", short_name="Неакт", is_active=False)

        queryset = get_active_organizations_queryset()
        self.assertEqual(queryset.count(), 1)

    def test_get_organizations_with_active_teacher_registration_code_queryset(self):
        organization = create_organization(name="С кодом", short_name="СК")
        create_organization(name="Без кода", short_name="БК")
        activate_teacher_registration_code(
            organization,
            raw_code="ORG-CODE-123",
            expires_at=timezone.now() + timedelta(days=1),
        )

        queryset = get_organizations_with_active_teacher_registration_code_queryset()
        self.assertEqual(queryset.count(), 1)
        self.assertIn(organization, queryset)

    def test_get_organization_with_active_teacher_registration_code(self):
        organization = create_organization(name="С кодом 2", short_name="СК2")
        activate_teacher_registration_code(
            organization,
            raw_code="ORG-CODE-456",
            expires_at=timezone.now() + timedelta(days=1),
        )

        result = get_organization_with_active_teacher_registration_code(organization.id)
        self.assertEqual(result.id, organization.id)

    def test_get_departments_queryset(self):
        create_department()
        queryset = get_departments_queryset()

        self.assertEqual(queryset.count(), 1)

    def test_get_active_departments_queryset(self):
        create_department(name="Активное отделение", is_active=True)
        create_department(name="Неактивное отделение", short_name="Н/А", is_active=False)

        queryset = get_active_departments_queryset()
        self.assertEqual(queryset.count(), 1)

    def test_get_departments_by_organization_queryset(self):
        organization = create_organization()
        create_department(organization=organization, name="Отделение 1")
        create_department(organization=create_organization(), name="Отделение 2")

        queryset = get_departments_by_organization_queryset(organization.id)
        self.assertEqual(queryset.count(), 1)


class SubjectSelectorsTestCase(TestCase):
    def test_get_subject_categories_queryset(self):
        create_subject_category(code="math", name="Математика")
        queryset = get_subject_categories_queryset()

        self.assertEqual(queryset.count(), 1)

    def test_get_active_subject_categories_queryset(self):
        create_subject_category(code="active_math", name="Активная математика", is_active=True)
        create_subject_category(code="inactive_math", name="Неактивная математика", is_active=False)

        queryset = get_active_subject_categories_queryset()
        self.assertEqual(queryset.count(), 1)

    def test_get_subjects_queryset(self):
        create_subject(name="Алгебра")
        queryset = get_subjects_queryset()

        self.assertEqual(queryset.count(), 1)

    def test_get_active_subjects_queryset(self):
        create_subject(name="Активный предмет", short_name="Акт", is_active=True)
        create_subject(name="Неактивный предмет", short_name="Неакт", is_active=False)

        queryset = get_active_subjects_queryset()
        self.assertEqual(queryset.count(), 1)


class GroupSelectorsTestCase(TestCase):
    def test_get_groups_queryset(self):
        create_group(name="ИСП-51", code="ISP-51")
        queryset = get_groups_queryset()

        self.assertEqual(queryset.count(), 1)

    def test_get_active_groups_queryset(self):
        create_group(name="ИСП-52", code="ISP-52", is_active=True)
        create_group(name="ИСП-53", code="ISP-53", is_active=False)

        queryset = get_active_groups_queryset()
        self.assertEqual(queryset.count(), 1)

    def test_get_groups_by_organization_queryset(self):
        organization = create_organization()
        create_group(organization=organization, name="Группа 1", code="G-1")
        create_group(organization=create_organization(), name="Группа 2", code="G-2")

        queryset = get_groups_by_organization_queryset(organization.id)
        self.assertEqual(queryset.count(), 1)

    def test_get_groups_by_department_queryset(self):
        organization = create_organization()
        department = create_department(organization=organization)
        create_group(organization=organization, department=department, name="Группа 1", code="GD-1")
        create_group(organization=organization, department=create_department(organization=organization), name="Группа 2", code="GD-2")

        queryset = get_groups_by_department_queryset(department.id)
        self.assertEqual(queryset.count(), 1)

    def test_get_groups_with_active_join_code_queryset(self):
        group = create_group(name="ИСП-54", code="ISP-54")
        create_group(name="ИСП-55", code="ISP-55")
        activate_group_join_code(
            group,
            raw_code="JOIN-123456",
            expires_at=timezone.now() + timedelta(days=1),
        )

        queryset = get_groups_with_active_join_code_queryset()
        self.assertEqual(queryset.count(), 1)
        self.assertIn(group, queryset)

    def test_get_group_with_active_join_code(self):
        group = create_group(name="ИСП-56", code="ISP-56")
        activate_group_join_code(
            group,
            raw_code="JOIN-654321",
            expires_at=timezone.now() + timedelta(days=1),
        )

        result = get_group_with_active_join_code(group.id)
        self.assertEqual(result.id, group.id)

    def test_get_group_curators_queryset(self):
        group = create_group()
        teacher = create_teacher_user()
        create_group_curator(group=group, teacher=teacher)

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

    def test_get_teacher_organizations_queryset(self):
        teacher = create_teacher_user()
        organization = create_organization()
        create_teacher_organization(teacher=teacher, organization=organization)

        queryset = get_teacher_organizations_queryset()
        self.assertEqual(queryset.count(), 1)

    def test_get_active_teacher_organizations_queryset(self):
        teacher = create_teacher_user()
        active_link = create_teacher_organization(
            teacher=teacher,
            organization=create_organization(name="Орг А", short_name="А"),
            is_active=True,
            starts_at=date.today() - timedelta(days=1),
            ends_at=date.today() + timedelta(days=1),
        )
        create_teacher_organization(
            teacher=teacher,
            organization=create_organization(name="Орг Б", short_name="Б"),
            is_active=False,
            starts_at=date.today() - timedelta(days=10),
            ends_at=date.today() - timedelta(days=1),
        )

        queryset = get_active_teacher_organizations_queryset(teacher_id=teacher.id)
        self.assertEqual(queryset.count(), 1)
        self.assertIn(active_link, queryset)

    def test_get_teacher_subjects_queryset(self):
        teacher = create_teacher_user()
        subject = create_subject()
        create_teacher_subject(teacher=teacher, subject=subject)

        queryset = get_teacher_subjects_queryset()
        self.assertEqual(queryset.count(), 1)
