from __future__ import annotations

from django.urls import reverse
from rest_framework import status

from apps.organizations.tests.test_api.api_base import OrganizationApiBaseTestCase
from apps.organizations.tests.factories import (
    create_organization,
    create_subject,
    create_teacher_organization,
    create_teacher_subject,
    create_teacher_user,
)


class OrganizationTeacherOrganizationApiTestCase(OrganizationApiBaseTestCase):
    """Тесты API связей преподавателей с организациями."""

    def test_teacher_organization_list(self):
        teacher = create_teacher_user()
        organization = create_organization()
        create_teacher_organization(
            teacher=teacher,
            organization=organization,
        )

        url = reverse("organizations:teacher-organization-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_teacher_organization_with_position(self):
        teacher = create_teacher_user()
        organization = create_organization()

        url = reverse("organizations:teacher-organization-list")
        payload = {
            "teacher_id": teacher.id,
            "organization_id": organization.id,
            "position": "Преподаватель информатики",
            "employment_type": "main",
            "is_primary": True,
            "is_active": True,
        }

        response = self.client.post(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["position"], "Преподаватель информатики")
        self.assertTrue(response.data["is_primary"])

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

        url = reverse(
            "organizations:teacher-organization-set-primary",
            args=[link_2.id],
        )
        response = self.client.post(url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["is_primary"])

    def test_delete_teacher_organization_soft_deactivates(self):
        teacher = create_teacher_user()
        organization = create_organization()
        link = create_teacher_organization(
            teacher=teacher,
            organization=organization,
            is_primary=True,
            is_active=True,
        )

        url = reverse(
            "organizations:teacher-organization-detail",
            args=[link.id],
        )
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        link.refresh_from_db()
        self.assertFalse(link.is_active)
        self.assertFalse(link.is_primary)


class OrganizationTeacherSubjectApiTestCase(OrganizationApiBaseTestCase):
    """Тесты API связей преподавателей с предметами."""

    def test_teacher_subject_list(self):
        teacher = create_teacher_user()
        subject = create_subject()
        create_teacher_subject(
            teacher=teacher,
            subject=subject,
        )

        url = reverse("organizations:teacher-subject-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
