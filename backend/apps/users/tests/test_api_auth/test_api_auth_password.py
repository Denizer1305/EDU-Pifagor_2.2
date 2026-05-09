from __future__ import annotations

from unittest.mock import patch

from django.urls import reverse
from rest_framework import status

from apps.users.services.auth_services import build_password_reset_token
from apps.users.tests.test_api_auth.api_auth_base import (
    AuthApiBaseTestCase,
)


class AuthPasswordApiTestCase(AuthApiBaseTestCase):
    """API-тесты восстановления и смены пароля."""

    @patch("apps.users.views.auth.password.send_reset_password_email_task.delay")
    def test_password_reset_request_existing_user_returns_200(
        self,
        mock_send_reset_email,
    ):
        user = self.create_user(
            email="reset-request@xample.com",
            password=self.password,
        )

        url = reverse("users:password-reset")
        response = self.client.post(
            url,
            data={
                "email": user.email,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_send_reset_email.assert_called_once()

    @patch("apps.users.views.auth.password.send_reset_password_email_task.delay")
    def test_password_reset_request_unknown_user_still_returns_200(
        self,
        mock_send_reset_email,
    ):
        url = reverse("users:password-reset")

        response = self.client.post(
            url,
            data={
                "email": "unknown-reset@example.com",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_send_reset_email.assert_not_called()

    @patch("apps.users.views.auth.password.send_password_changed_email_task.delay")
    def test_password_reset_confirm_success(self, mock_send_password_changed):
        user = self.create_user(
            email="reset-confirm@example.com",
            password=self.password,
        )
        token = build_password_reset_token(user)

        url = reverse("users:password-reset-confirm")
        response = self.client.post(
            url,
            data={
                "token": token,
                "password": "NewStrongPass123!",
                "password_repeat": "NewStrongPass123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        user.refresh_from_db()
        self.assertTrue(user.check_password("NewStrongPass123!"))
        mock_send_password_changed.assert_called_once_with(user.id)

    def test_password_reset_confirm_without_token_returns_400(self):
        url = reverse("users:password-reset-confirm")

        response = self.client.post(
            url,
            data={
                "password": "NewStrongPass123!",
                "password_repeat": "NewStrongPass123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("token", response.data)

    def test_password_reset_confirm_password_mismatch_returns_400(self):
        user = self.create_user(
            email="reset-mismatch@example.com",
            password=self.password,
        )
        token = build_password_reset_token(user)

        url = reverse("users:password-reset-confirm")
        response = self.client.post(
            url,
            data={
                "token": token,
                "password": "NewStrongPass123!",
                "password_repeat": "AnotherStrongPass123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password_repeat", response.data)

    @patch("apps.users.views.auth.password.send_password_changed_email_task.delay")
    def test_change_password_success(self, mock_send_password_changed):
        user = self.create_user(
            email="change-password@example.com",
            password=self.password,
        )
        self.client.force_authenticate(user=user)

        url = reverse("users:change-password")
        response = self.client.post(
            url,
            data={
                "old_password": self.password,
                "new_password": "ChangedStrong123!",
                "new_password_confirm": "ChangedStrong123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        user.refresh_from_db()
        self.assertTrue(user.check_password("ChangedStrong123!"))
        mock_send_password_changed.assert_called_once_with(user.id)

    def test_change_password_wrong_old_password_returns_400(self):
        user = self.create_user(
            email="change-wrong-old@example.com",
            password=self.password,
        )
        self.client.force_authenticate(user=user)

        url = reverse("users:change-password")
        response = self.client.post(
            url,
            data={
                "old_password": "WrongStrongPass123!",
                "new_password": "ChangedStrong123!",
                "new_password_confirm": "ChangedStrong123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("old_password", response.data)

    def test_change_password_requires_authentication(self):
        url = reverse("users:change-password")

        response = self.client.post(
            url,
            data={
                "old_password": self.password,
                "new_password": "ChangedStrong123!",
                "new_password_confirm": "ChangedStrong123!",
            },
            format="json",
        )

        self.assertIn(
            response.status_code,
            {
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_403_FORBIDDEN,
            },
        )
