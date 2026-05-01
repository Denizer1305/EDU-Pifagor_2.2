from __future__ import annotations

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status

from apps.users.tests.test_api_auth.api_auth_base import AuthApiBaseTestCase

User = get_user_model()


class AuthSessionApiTestCase(AuthApiBaseTestCase):
    """API-тесты входа и выхода пользователя."""

    def test_login_success(self):
        user = self.create_user(
            email="login-success@example.com",
            password=self.password,
        )

        url = reverse("users:login")
        response = self.client.post(
            url,
            data={
                "email": user.email,
                "password": self.password,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], user.email)

    def test_login_wrong_password_returns_400(self):
        user = self.create_user(
            email="login-wrong-password@example.com",
            password=self.password,
        )

        url = reverse("users:login")
        response = self.client.post(
            url,
            data={
                "email": user.email,
                "password": "WrongStrongPass123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", response.data)

    def test_login_blocked_user_returns_400(self):
        user = self.create_user(
            email="login-blocked@example.com",
            password=self.password,
            onboarding_status=User.OnboardingStatusChoices.BLOCKED,
        )

        url = reverse("users:login")
        response = self.client.post(
            url,
            data={
                "email": user.email,
                "password": self.password,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", response.data)

    def test_logout_success(self):
        user = self.create_user(
            email="logout-user@example.com",
            password=self.password,
        )
        self.client.force_authenticate(user=user)

        url = reverse("users:logout")
        response = self.client.post(url, data={}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("detail", response.data)

    def test_logout_requires_authentication(self):
        url = reverse("users:logout")
        response = self.client.post(url, data={}, format="json")

        self.assertIn(
            response.status_code,
            {
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_403_FORBIDDEN,
            },
        )
