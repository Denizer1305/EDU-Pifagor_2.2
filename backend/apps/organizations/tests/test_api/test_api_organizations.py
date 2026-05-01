from __future__ import annotations

from django.urls import reverse
from rest_framework import status

from apps.organizations.tests.test_api.api_base import OrganizationApiBaseTestCase
from apps.organizations.tests.factories import (
    create_department,
    create_organization,
    create_organization_type,
)


class OrganizationDirectoryApiTestCase(OrganizationApiBaseTestCase):
    """Тесты API типов организаций, организаций и подразделений."""

    def test_organization_type_list(self):
        create_organization_type(code="college", name="Колледж")

        url = reverse("organizations:organization-type-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_organization_list(self):
        create_organization(name="Колледж Пифагор", short_name="Пифагор")

        url = reverse("organizations:organization-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_department_list(self):
        create_department()

        url = reverse("organizations:department-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_organization(self):
        organization_type = create_organization_type(
            code="school",
            name="Школа",
        )

        url = reverse("organizations:organization-list")
        payload = {
            "type_id": organization_type.id,
            "name": "Новая школа",
            "short_name": "Школа №1",
            "city": "Москва",
            "is_active": True,
        }

        response = self.client.post(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "Новая школа")


class OrganizationTeacherRegistrationCodeApiTestCase(OrganizationApiBaseTestCase):
    """Тесты API кода регистрации преподавателя в организации."""

    def test_set_teacher_registration_code(self):
        organization = create_organization()

        url = reverse(
            "organizations:organization-teacher-registration-code",
            args=[organization.id],
        )
        payload = {
            "teacher_registration_code": "TEACHER-API-123",
        }

        response = self.client.post(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["teacher_registration_code_is_active"])
        self.assertTrue(response.data["has_active_teacher_registration_code"])

    def test_disable_teacher_registration_code(self):
        organization = create_organization()
        organization.set_teacher_registration_code("TEACHER-DISABLE-123")
        organization.save()

        url = reverse(
            "organizations:organization-teacher-registration-code-disable",
            args=[organization.id],
        )
        response = self.client.post(url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["teacher_registration_code_is_active"])

    def test_clear_teacher_registration_code(self):
        organization = create_organization()
        organization.set_teacher_registration_code("TEACHER-CLEAR-123")
        organization.save()

        url = reverse(
            "organizations:organization-teacher-registration-code",
            args=[organization.id],
        )
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["teacher_registration_code_is_active"])
        self.assertFalse(response.data["has_active_teacher_registration_code"])
