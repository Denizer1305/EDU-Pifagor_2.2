from __future__ import annotations

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.users.tests.factories import create_profile, create_user


class ProfileApiTestCase(APITestCase):
    def test_my_profile_get(self):
        user = create_user(email="profileme@example.com", password="TestPass123!")
        create_profile(
            user=user,
            email="profileme@example.com",
            first_name="Мария",
            last_name="Петрова",
            patronymic="Александровна",
        )
        self.client.force_authenticate(user=user)

        url = reverse("users:my-profile")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["first_name"], "Мария")
        self.assertEqual(response.data["last_name"], "Петрова")
        self.assertEqual(response.data["patronymic"], "Александровна")
        self.assertEqual(response.data["email"], "profileme@example.com")

    def test_my_profile_patch(self):
        user = create_user(email="patchprofile@example.com", password="TestPass123!")
        create_profile(
            user=user,
            email="patchprofile@example.com",
            first_name="Мария",
            last_name="Петрова",
            patronymic="Александровна",
        )
        self.client.force_authenticate(user=user)

        url = reverse("users:my-profile")
        payload = {
            "city": "Санкт-Петербург",
            "about": "Новый текст профиля",
        }

        response = self.client.patch(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        user.profile.refresh_from_db()
        self.assertEqual(user.profile.city, "Санкт-Петербург")
        self.assertEqual(user.profile.about, "Новый текст профиля")

    def test_my_profile_requires_auth(self):
        url = reverse("users:my-profile")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_profile_detail_get(self):
        user = create_user(email="profiledetail@example.com", password="TestPass123!")
        profile = create_profile(
            user=user,
            email="profiledetail@example.com",
            first_name="Ольга",
            last_name="Смирнова",
            patronymic="Игоревна",
        )

        auth_user = create_user(email="viewer@example.com", password="TestPass123!")
        create_profile(user=auth_user, email="viewer@example.com")
        self.client.force_authenticate(user=auth_user)

        url = reverse("users:profile-detail", kwargs={"pk": profile.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["first_name"], "Ольга")
        self.assertEqual(response.data["last_name"], "Смирнова")
        self.assertEqual(response.data["patronymic"], "Игоревна")

    def test_profile_detail_requires_auth(self):
        user = create_user(email="profiledetail2@example.com", password="TestPass123!")
        profile = create_profile(user=user, email="profiledetail2@example.com")

        url = reverse("users:profile-detail", kwargs={"pk": profile.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
