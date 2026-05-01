from __future__ import annotations

from unittest.mock import patch

from django.urls import reverse
from rest_framework import status

from apps.users.services.auth_services import build_verify_email_token
from apps.users.tests.test_api_auth.api_auth_base import AuthApiBaseTestCase


class AuthEmailApiTestCase(AuthApiBaseTestCase):
    """API-тесты подтверждения email."""

    @patch("apps.users.views.auth.email.send_welcome_email_task.delay")
    def test_verify_email_success(self, mock_send_welcome_email):
        user = self.create_user(
            email="verify-email@example.com",
            password=self.password,
            is_email_verified=False,
        )
        token = build_verify_email_token(user)

        url = reverse("users:verify-email")
        response = self.client.post(
            url,
            data={
                "token": token,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        user.refresh_from_db()
        self.assertTrue(user.is_email_verified)
        mock_send_welcome_email.assert_called_once_with(user.id)

    def test_verify_email_without_token_returns_400(self):
        url = reverse("users:verify-email")

        response = self.client.post(
            url,
            data={},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("token", response.data)
