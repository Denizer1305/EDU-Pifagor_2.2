from __future__ import annotations

from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.organizations.models import Group
from apps.organizations.tests.factories import (
    create_department,
    create_group,
    create_organization,
    create_organization_type,
    create_subject,
    create_subject_category,
    create_teacher_organization,
    create_teacher_subject,
    create_teacher_user,
)


class OrganizationTypeModelTestCase(TestCase):
    def test_create_organization_type(self):
        organization_type = create_organization_type(
            code="school",
            name="Школа",
        )

        self.assertEqual(organization_type.code, "school")
        self.assertEqual(str(organization_type), "Школа")


class OrganizationModelTestCase(TestCase):
    def test_create_organization(self):
        organization = create_organization(name="Колледж Пифагор", short_name="Пифагор")

        self.assertEqual(organization.name, "Колледж Пифагор")
        self.assertEqual(str(organization), "Пифагор")


class DepartmentModelTestCase(TestCase):
    def test_create_department(self):
        department = create_department(name="Факультет математики", short_name="Матфак")

        self.assertEqual(department.name, "Факультет математики")
        self.assertIn("Матфак", str(department))


class SubjectCategoryModelTestCase(TestCase):
    def test_create_subject_category(self):
        category = create_subject_category(code="math", name="Математика")

        self.assertEqual(category.code, "math")
        self.assertEqual(str(category), "Математика")


class SubjectModelTestCase(TestCase):
    def test_create_subject(self):
        subject = create_subject(name="Алгебра", short_name="Алгебра")

        self.assertEqual(subject.name, "Алгебра")
        self.assertEqual(str(subject), "Алгебра")


class GroupModelTestCase(TestCase):
    def test_create_group(self):
        group = create_group(name="ИСП-22", code="ISP-22")

        self.assertEqual(group.name, "ИСП-22")
        self.assertEqual(group.code, "ISP-22")
        self.assertIn("ИСП-22", str(group))

    def test_group_department_must_belong_to_same_organization(self):
        organization_1 = create_organization(name="Организация 1", short_name="Орг1")
        organization_2 = create_organization(name="Организация 2", short_name="Орг2")
        department = create_department(organization=organization_2)

        group = Group(
            organization=organization_1,
            department=department,
            name="Группа A",
            code="A-01",
        )

        with self.assertRaises(ValidationError):
            group.clean()


class TeacherOrganizationModelTestCase(TestCase):
    def test_create_teacher_organization(self):
        teacher = create_teacher_user()
        organization = create_organization()

        link = create_teacher_organization(
            teacher=teacher,
            organization=organization,
        )

        self.assertEqual(link.teacher, teacher)
        self.assertEqual(link.organization, organization)


class TeacherSubjectModelTestCase(TestCase):
    def test_create_teacher_subject(self):
        teacher = create_teacher_user()
        subject = create_subject()

        link = create_teacher_subject(
            teacher=teacher,
            subject=subject,
        )

        self.assertEqual(link.teacher, teacher)
        self.assertEqual(link.subject, subject)
