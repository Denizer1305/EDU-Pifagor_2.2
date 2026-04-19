from __future__ import annotations

from django.test import TestCase

from apps.organizations.selectors import (
    get_active_departments_queryset,
    get_active_groups_queryset,
    get_active_organization_types_queryset,
    get_active_organizations_queryset,
    get_active_subject_categories_queryset,
    get_active_subjects_queryset,
    get_departments_queryset,
    get_group_curators_queryset,
    get_groups_queryset,
    get_organization_types_queryset,
    get_organizations_queryset,
    get_subject_categories_queryset,
    get_subjects_queryset,
    get_teacher_organizations_queryset,
    get_teacher_subjects_queryset,
)
from apps.organizations.tests.factories import (
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

    def test_get_departments_queryset(self):
        create_department()
        queryset = get_departments_queryset()

        self.assertEqual(queryset.count(), 1)

    def test_get_active_departments_queryset(self):
        create_department(name="Активное отделение", is_active=True)
        create_department(name="Неактивное отделение", short_name="Н/А", is_active=False)

        queryset = get_active_departments_queryset()
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

    def test_get_group_curators_queryset(self):
        group = create_group()
        teacher = create_teacher_user()
        create_group_curator(group=group, teacher=teacher)

        queryset = get_group_curators_queryset()
        self.assertEqual(queryset.count(), 1)

    def test_get_teacher_organizations_queryset(self):
        teacher = create_teacher_user()
        organization = create_organization()
        create_teacher_organization(teacher=teacher, organization=organization)

        queryset = get_teacher_organizations_queryset()
        self.assertEqual(queryset.count(), 1)

    def test_get_teacher_subjects_queryset(self):
        teacher = create_teacher_user()
        subject = create_subject()
        create_teacher_subject(teacher=teacher, subject=subject)

        queryset = get_teacher_subjects_queryset()
        self.assertEqual(queryset.count(), 1)
