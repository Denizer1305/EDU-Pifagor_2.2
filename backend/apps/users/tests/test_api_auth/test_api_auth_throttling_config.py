from __future__ import annotations

from django.test import SimpleTestCase
from rest_framework.throttling import ScopedRateThrottle

from apps.users.views.auth.email import VerifyEmailAPIView
from apps.users.views.auth.password import (
    ChangePasswordAPIView,
    PasswordResetConfirmAPIView,
    PasswordResetRequestAPIView,
)
from apps.users.views.auth.registration import RegisterAPIView
from apps.users.views.auth.session import LoginAPIView


class AuthThrottlingConfigTestCase(SimpleTestCase):
    """Проверяет, что security-sensitive auth endpoints имеют scoped throttling."""

    def assert_scoped_throttle(self, view_class, expected_scope: str) -> None:
        self.assertEqual(view_class.throttle_scope, expected_scope)
        self.assertIn(ScopedRateThrottle, view_class.throttle_classes)

    def test_login_has_scoped_throttling(self):
        self.assert_scoped_throttle(LoginAPIView, "auth_login")

    def test_register_has_scoped_throttling(self):
        self.assert_scoped_throttle(RegisterAPIView, "auth_register")

    def test_password_reset_request_has_scoped_throttling(self):
        self.assert_scoped_throttle(PasswordResetRequestAPIView, "password_reset")

    def test_password_reset_confirm_has_scoped_throttling(self):
        self.assert_scoped_throttle(
            PasswordResetConfirmAPIView,
            "password_reset_confirm",
        )

    def test_change_password_has_scoped_throttling(self):
        self.assert_scoped_throttle(ChangePasswordAPIView, "password_change")

    def test_verify_email_has_scoped_throttling(self):
        self.assert_scoped_throttle(VerifyEmailAPIView, "email_verify")
