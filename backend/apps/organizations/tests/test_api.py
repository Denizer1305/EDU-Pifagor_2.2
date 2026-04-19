from __future__ import annotations

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

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
from apps.users.tests.factories import create_admin_user


class OrganizationApiTestCase(APITestCase):
    def setUp(self):
        self.admin_user = create_admin_user()
        self.client.force_authenticate(user=self.admin_user)

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

    def test_subject_category_list(self):
        create_subject_category(code="math", name="Математика")

        url = reverse("organizations:subject-category-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_subject_list(self):
        create_subject(name="Алгебра", short_name="Алгебра")

        url = reverse("organizations:subject-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_group_list(self):
        create_group(name="ИСП-41", code="ISP-41")

        url = reverse("organizations:group-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_group_curator_list(self):
        group = create_group()
        teacher = create_teacher_user()
        from apps.organizations.tests.factories import create_group_curator

        create_group_curator(group=group, teacher=teacher)

        url = reverse("organizations:group-curator-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_teacher_organization_list(self):
        teacher = create_teacher_user()
        organization = create_organization()
        create_teacher_organization(teacher=teacher, organization=organization)

        url = reverse("organizations:teacher-organization-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_teacher_subject_list(self):
        teacher = create_teacher_user()
        subject = create_subject()
        create_teacher_subject(teacher=teacher, subject=subject)

        url = reverse("organizations:teacher-subject-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_organization(self):
        organization_type = create_organization_type(code="school", name="Школа")

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
