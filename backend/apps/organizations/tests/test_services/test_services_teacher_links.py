from __future__ import annotations

from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.organizations.models import TeacherOrganization, TeacherSubject
from apps.organizations.services import (
    assign_teacher_subject,
    assign_teacher_to_organization,
    remove_teacher_from_organization,
    remove_teacher_subject,
    set_primary_teacher_organization,
)
from apps.organizations.tests.factories import (
    create_non_teacher_user,
    create_organization,
    create_subject,
    create_teacher_organization,
    create_teacher_user,
)


class TeacherOrganizationServicesTestCase(TestCase):
    def test_assign_teacher_to_organization(self):
        teacher = create_teacher_user()
        organization = create_organization()

        link = assign_teacher_to_organization(
            teacher=teacher,
            organization=organization,
            position="Преподаватель математики",
            is_primary=True,
        )

        self.assertIsInstance(link, TeacherOrganization)
        self.assertEqual(link.teacher, teacher)
        self.assertEqual(link.organization, organization)
        self.assertEqual(link.position, "Преподаватель математики")
        self.assertTrue(link.is_primary)

    def test_assign_non_teacher_to_organization_raises_error(self):
        user = create_non_teacher_user()
        organization = create_organization()

        with self.assertRaises(ValidationError):
            assign_teacher_to_organization(
                teacher=user,
                organization=organization,
            )

    def test_set_primary_teacher_organization(self):
        teacher = create_teacher_user()
        organization_1 = create_organization(
            name="Организация 1",
            short_name="Орг1",
        )
        organization_2 = create_organization(
            name="Организация 2",
            short_name="Орг2",
        )

        create_teacher_organization(
            teacher=teacher,
            organization=organization_1,
            is_primary=True,
            is_active=True,
        )
        link_2 = create_teacher_organization(
            teacher=teacher,
            organization=organization_2,
            is_primary=False,
            is_active=True,
        )

        updated_link = set_primary_teacher_organization(
            teacher=teacher,
            organization=organization_2,
        )

        self.assertEqual(updated_link.id, link_2.id)
        self.assertTrue(updated_link.is_primary)

    def test_remove_teacher_from_organization_soft_deactivates_link(self):
        teacher = create_teacher_user()
        organization = create_organization()

        link = assign_teacher_to_organization(
            teacher=teacher,
            organization=organization,
            is_primary=True,
            is_active=True,
        )

        remove_teacher_from_organization(
            teacher=teacher,
            organization=organization,
        )

        link.refresh_from_db()
        self.assertFalse(link.is_active)
        self.assertFalse(link.is_primary)


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

    def test_remove_teacher_subject_soft_deactivates_link(self):
        teacher = create_teacher_user()
        subject = create_subject()

        link = assign_teacher_subject(
            teacher=teacher,
            subject=subject,
            is_primary=True,
            is_active=True,
        )

        remove_teacher_subject(
            teacher=teacher,
            subject=subject,
        )

        link.refresh_from_db()
        self.assertFalse(link.is_active)
        self.assertFalse(link.is_primary)
