from __future__ import annotations

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.users.tests.factories import create_admin_user, create_profile, create_user


class UserApiTestCase(APITestCase):
    def test_user_list_available_for_admin(self):
        admin_user = create_admin_user()

        simple_user = create_user(email="simple1@example.com", password="TestPass123!")
        create_profile(user=simple_user, email="simple1@example.com")

        self.client.force_authenticate(user=admin_user)

        url = reverse("users:user-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        if isinstance(response.data, dict) and "results" in response.data:
            self.assertGreaterEqual(len(response.data["results"]), 1)
        else:
            self.assertGreaterEqual(len(response.data), 1)

    def test_user_list_forbidden_for_regular_user(self):
        user = create_user(email="simple2@example.com", password="TestPass123!")
        create_profile(user=user, email="simple2@example.com")

        self.client.force_authenticate(user=user)

        url = reverse("users:user-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_detail_available_for_admin(self):
        admin_user = create_admin_user()

        target_user = create_user(email="target@example.com", password="TestPass123!")
        create_profile(user=target_user, email="target@example.com")

        self.client.force_authenticate(user=admin_user)

        url = reverse("users:user-detail", kwargs={"pk": target_user.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "target@example.com")

    def test_user_detail_patch_for_admin(self):
        admin_user = create_admin_user()

        target_user = create_user(email="target2@example.com", password="TestPass123!")
        create_profile(user=target_user, email="target2@example.com")

        self.client.force_authenticate(user=admin_user)

        url = reverse("users:user-detail", kwargs={"pk": target_user.pk})
        payload = {
            "reset_email": "backup@example.com",
            "is_email_verified": True,
        }

        response = self.client.patch(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        target_user.refresh_from_db()
        self.assertEqual(target_user.reset_email, "backup@example.com")
        self.assertTrue(target_user.is_email_verified)

    def test_user_detail_forbidden_for_regular_user(self):
        regular_user = create_user(email="regular@example.com", password="TestPass123!")
        create_profile(user=regular_user, email="regular@example.com")

        target_user = create_user(email="target3@example.com", password="TestPass123!")
        create_profile(user=target_user, email="target3@example.com")

        self.client.force_authenticate(user=regular_user)

        url = reverse("users:user-detail", kwargs={"pk": target_user.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
