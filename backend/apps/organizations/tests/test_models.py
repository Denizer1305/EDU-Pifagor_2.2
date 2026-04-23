from __future__ import annotations

from datetime import date, timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from apps.organizations.models import Group, GroupCurator, Organization, TeacherOrganization
from apps.organizations.tests.factories import (
    activate_group_join_code,
    activate_teacher_registration_code,
    create_department,
    create_group,
    create_group_curator,
    create_non_teacher_user,
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

    def test_teacher_registration_code_can_be_set_and_verified(self):
        organization = create_organization()
        activate_teacher_registration_code(
            organization,
            raw_code="TEACH-777",
            expires_at=timezone.now() + timedelta(days=1),
        )

        self.assertTrue(organization.has_active_teacher_registration_code)
        self.assertTrue(organization.verify_teacher_registration_code("TEACH-777"))
        self.assertFalse(organization.verify_teacher_registration_code("WRONG-CODE"))
        self.assertNotEqual(organization.teacher_registration_code_hash, "TEACH-777")

    def test_teacher_registration_code_not_active_when_expired(self):
        organization = create_organization()
        activate_teacher_registration_code(
            organization,
            raw_code="TEACH-888",
            expires_at=timezone.now() - timedelta(days=1),
        )

        self.assertFalse(organization.has_active_teacher_registration_code)


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

    def test_group_join_code_can_be_set_and_verified(self):
        group = create_group()
        activate_group_join_code(
            group,
            raw_code="GROUP-12345",
            expires_at=timezone.now() + timedelta(days=1),
        )

        self.assertTrue(group.has_active_join_code)
        self.assertTrue(group.verify_join_code("GROUP-12345"))
        self.assertFalse(group.verify_join_code("WRONG-CODE"))
        self.assertNotEqual(group.join_code_hash, "GROUP-12345")

    def test_group_join_code_not_active_when_expired(self):
        group = create_group()
        activate_group_join_code(
            group,
            raw_code="GROUP-EXPIRED",
            expires_at=timezone.now() - timedelta(days=1),
        )

        self.assertFalse(group.has_active_join_code)


class GroupCuratorModelTestCase(TestCase):
    def test_group_curator_is_current(self):
        curator = create_group_curator(
            starts_at=date.today() - timedelta(days=1),
            ends_at=date.today() + timedelta(days=1),
            is_active=True,
        )

        self.assertTrue(curator.is_current)

    def test_group_curator_clean_rejects_non_teacher(self):
        group = create_group()
        user = create_non_teacher_user()

        curator = GroupCurator(
            group=group,
            teacher=user,
            is_primary=True,
            is_active=True,
        )

        with self.assertRaises(ValidationError):
            curator.clean()


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

    def test_teacher_organization_is_current(self):
        link = create_teacher_organization(
            starts_at=date.today() - timedelta(days=10),
            ends_at=date.today() + timedelta(days=10),
            is_active=True,
        )

        self.assertTrue(link.is_current)

    def test_teacher_organization_primary_must_be_active(self):
        teacher = create_teacher_user()
        organization = create_organization()

        link = TeacherOrganization(
            teacher=teacher,
            organization=organization,
            is_primary=True,
            is_active=False,
        )

        with self.assertRaises(ValidationError):
            link.clean()

    def test_teacher_organization_cannot_have_two_active_primary_links(self):
        teacher = create_teacher_user()
        organization_1 = create_organization(name="Организация 1", short_name="Орг1")
        organization_2 = create_organization(name="Организация 2", short_name="Орг2")

        create_teacher_organization(
            teacher=teacher,
            organization=organization_1,
            is_primary=True,
            is_active=True,
        )

        link = TeacherOrganization(
            teacher=teacher,
            organization=organization_2,
            is_primary=True,
            is_active=True,
        )

        with self.assertRaises(ValidationError):
            link.clean()


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
