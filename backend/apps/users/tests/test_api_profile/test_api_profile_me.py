from __future__ import annotations

from django.urls import reverse
from rest_framework import status

from apps.users.tests.test_api_profile.api_profile_base import ProfileApiBaseTestCase


class MyProfileApiTestCase(ProfileApiBaseTestCase):
    """API-тесты личного профиля пользователя."""

    def test_my_profile_get(self):
        self.client.force_authenticate(user=self.student)
        url = reverse("users:my-profile")

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.student.email)

    def test_my_profile_patch(self):
        self.client.force_authenticate(user=self.student)
        url = reverse("users:my-profile")

        payload = {
            "first_name": "Обновленное",
            "last_name": "Имя",
            "city": "Москва",
            "phone": "+79995554433",
        }

        response = self.client.patch(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.student.profile.refresh_from_db()
        self.assertEqual(self.student.profile.city, "Москва")
        self.assertEqual(self.student.profile.first_name, "Обновленное")
