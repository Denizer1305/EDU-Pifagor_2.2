from __future__ import annotations

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

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

    def test_set_group_join_code(self):
        group = create_group()

        url = reverse(
            "organizations:group-join-code",
            args=[group.id],
        )
        payload = {
            "join_code": "GROUP-API-123",
        }

        response = self.client.post(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["join_code_is_active"])
        self.assertTrue(response.data["has_active_join_code"])

    def test_clear_group_join_code(self):
        group = create_group()
        group.set_join_code("GROUP-CLEAR-123")
        group.save()

        url = reverse(
            "organizations:group-join-code",
            args=[group.id],
        )
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["join_code_is_active"])
        self.assertFalse(response.data["has_active_join_code"])

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

    def test_delete_group_curator_soft_deactivates(self):
        group = create_group()
        teacher = create_teacher_user()
        curator = create_group_curator(
            group=group,
            teacher=teacher,
            is_primary=True,
            is_active=True,
        )

        url = reverse(
            "organizations:group-curator-detail",
            args=[curator.id],
        )
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        curator.refresh_from_db()
        self.assertFalse(curator.is_active)
        self.assertFalse(curator.is_primary)
