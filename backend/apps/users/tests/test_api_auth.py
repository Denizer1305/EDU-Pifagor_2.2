from __future__ import annotations

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.users.models import Profile
from apps.users.tests.factories import create_profile, create_user

User = get_user_model()


class AuthApiTestCase(APITestCase):
    def test_register(self):
        url = reverse("users:register")
        payload = {
            "email": "registered@example.com",
            "phone": "+79990000002",
            "password": "TestPass123!",
            "password_repeat": "TestPass123!",
            "first_name": "Иван",
            "last_name": "Иванов",
            "patronymic": "Иванович",
        }

        response = self.client.post(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email="registered@example.com").exists())

        user = User.objects.get(email="registered@example.com")
        self.assertTrue(Profile.objects.filter(user=user).exists())

    def test_register_fails_if_passwords_do_not_match(self):
        url = reverse("users:register")
        payload = {
            "email": "registered2@example.com",
            "phone": "+79990000003",
            "password": "TestPass123!",
            "password_repeat": "WrongPass123!",
            "first_name": "Иван",
            "last_name": "Иванов",
            "patronymic": "Иванович",
        }

        response = self.client.post(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password_repeat", response.data["errors"])

    def test_login(self):
        user = create_user(email="login@example.com", password="TestPass123!")
        create_profile(user=user, email="login@example.com")

        url = reverse("users:login")
        payload = {
            "email": "login@example.com",
            "password": "TestPass123!",
        }

        response = self.client.post(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "login@example.com")

    def test_login_fails_with_wrong_password(self):
        user = create_user(email="wrongpass@example.com", password="TestPass123!")
        create_profile(user=user, email="wrongpass@example.com")

        url = reverse("users:login")
        payload = {
            "email": "wrongpass@example.com",
            "password": "WrongPassword!",
        }

        response = self.client.post(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", response.data["errors"])

    def test_me_requires_auth(self):
        url = reverse("users:me")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_me_returns_current_user(self):
        user = create_user(email="me@example.com", password="TestPass123!")
        create_profile(user=user, email="me@example.com")

        self.client.force_authenticate(user=user)

        url = reverse("users:me")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "me@example.com")

    def test_logout(self):
        user = create_user(email="logout@example.com", password="TestPass123!")
        create_profile(user=user, email="logout@example.com")
        self.client.force_authenticate(user=user)

        url = reverse("users:logout")
        response = self.client.post(url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_change_password(self):
        user = create_user(email="changepass@example.com", password="OldPass123!")
        create_profile(user=user, email="changepass@example.com")
        self.client.force_authenticate(user=user)

        url = reverse("users:change-password")
        payload = {
            "old_password": "OldPass123!",
            "new_password": "NewPass123!",
            "new_password_confirm": "NewPass123!",
        }

        response = self.client.post(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        user.refresh_from_db()
        self.assertTrue(user.check_password("NewPass123!"))

    def test_change_password_fails_if_old_password_invalid(self):
        user = create_user(email="changepass2@example.com", password="OldPass123!")
        create_profile(user=user, email="changepass2@example.com")
        self.client.force_authenticate(user=user)

        url = reverse("users:change-password")
        payload = {
            "old_password": "WrongOldPass!",
            "new_password": "NewPass123!",
            "new_password_confirm": "NewPass123!",
        }

        response = self.client.post(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("old_password", response.data["errors"])
