from __future__ import annotations

from datetime import date, timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from apps.organizations.models import GroupCurator, TeacherOrganization, TeacherSubject
from apps.organizations.services import (
    assign_group_curator,
    assign_teacher_subject,
    assign_teacher_to_organization,
    clear_group_join_code,
    clear_teacher_registration_code,
    create_group as create_group_service,
    disable_group_join_code,
    disable_teacher_registration_code,
    remove_group_curator,
    remove_teacher_from_organization,
    remove_teacher_subject,
    set_group_join_code,
    set_primary_teacher_organization,
    set_teacher_registration_code,
)
from apps.organizations.tests.factories import (
    create_department,
    create_group,
    create_non_teacher_user,
    create_organization,
    create_subject,
    create_teacher_organization,
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
        organization_1 = create_organization(name="Организация 1", short_name="Орг1")
        organization_2 = create_organization(name="Организация 2", short_name="Орг2")

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
