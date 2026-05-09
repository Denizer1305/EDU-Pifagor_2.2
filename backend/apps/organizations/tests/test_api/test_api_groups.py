from __future__ import annotations

from django.urls import reverse
from rest_framework import status

from apps.organizations.tests.factories import (
    create_group,
    create_group_curator,
    create_teacher_user,
)
from apps.organizations.tests.test_api.api_base import OrganizationApiBaseTestCase


class OrganizationGroupApiTestCase(OrganizationApiBaseTestCase):
    """Тесты API учебных групп."""

    def test_group_list(self):
        create_group(name="ИСП-41", code="ISP-41")

        url = reverse("organizations:group-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

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


class OrganizationGroupCuratorApiTestCase(OrganizationApiBaseTestCase):
    """Тесты API кураторов групп."""

    def test_group_curator_list(self):
        group = create_group()
        teacher = create_teacher_user()
        create_group_curator(group=group, teacher=teacher)

        url = reverse("organizations:group-curator-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

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
