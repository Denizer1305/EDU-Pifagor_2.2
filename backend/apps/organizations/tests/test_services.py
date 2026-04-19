from __future__ import annotations

from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.organizations.models import GroupCurator, TeacherOrganization, TeacherSubject
from apps.organizations.services import (
    assign_group_curator,
    assign_teacher_subject,
    assign_teacher_to_organization,
    create_group as create_group_service,
)
from apps.organizations.tests.factories import (
    create_department,
    create_group,
    create_non_teacher_user,
    create_organization,
    create_subject,
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
        organization_1 = create_organization(name="Организация 1", short_name="Орг1")
        organization_2 = create_organization(name="Организация 2", short_name="Орг2")
        department = create_department(organization=organization_2)

        with self.assertRaises(ValidationError):
            create_group_service(
                organization=organization_1,
                department=department,
                name="ИСП-32",
                code="ISP-32",
            )


class GroupCuratorServicesTestCase(TestCase):
    def test_assign_group_curator_for_teacher(self):
        group = create_group()
        teacher = create_teacher_user()

        curator = assign_group_curator(
            group=group,
            teacher=teacher,
            is_primary=True,
        )

        self.assertIsInstance(curator, GroupCurator)
        self.assertEqual(curator.group, group)
        self.assertEqual(curator.teacher, teacher)
        self.assertTrue(curator.is_primary)

    def test_assign_group_curator_for_non_teacher_raises_error(self):
        group = create_group()
        user = create_non_teacher_user()

        with self.assertRaises(ValidationError):
            assign_group_curator(
                group=group,
                teacher=user,
            )


class TeacherOrganizationServicesTestCase(TestCase):
    def test_assign_teacher_to_organization(self):
        teacher = create_teacher_user()
        organization = create_organization()

        link = assign_teacher_to_organization(
            teacher=teacher,
            organization=organization,
            is_primary=True,
        )

        self.assertIsInstance(link, TeacherOrganization)
        self.assertEqual(link.teacher, teacher)
        self.assertEqual(link.organization, organization)
        self.assertTrue(link.is_primary)

    def test_assign_non_teacher_to_organization_raises_error(self):
        user = create_non_teacher_user()
        organization = create_organization()

        with self.assertRaises(ValidationError):
            assign_teacher_to_organization(
                teacher=user,
                organization=organization,
            )


class TeacherSubjectServicesTestCase(TestCase):
    def test_assign_teacher_subject(self):
        teacher = create_teacher_user()
        subject = create_subject()

        link = assign_teacher_subject(
            teacher=teacher,
            subject=subject,
            is_primary=True,
        )

        self.assertIsInstance(link, TeacherSubject)
        self.assertEqual(link.teacher, teacher)
        self.assertEqual(link.subject, subject)
        self.assertTrue(link.is_primary)

    def test_assign_non_teacher_subject_raises_error(self):
        user = create_non_teacher_user()
        subject = create_subject()

        with self.assertRaises(ValidationError):
            assign_teacher_subject(
                teacher=user,
                subject=subject,
            )
