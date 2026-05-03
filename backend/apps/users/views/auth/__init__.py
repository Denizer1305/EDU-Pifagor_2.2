from __future__ import annotations

from .email import VerifyEmailAPIView
from .password import (
    ChangePasswordAPIView,
    PasswordResetConfirmAPIView,
    PasswordResetRequestAPIView,
)
from .registration import RegisterAPIView
from .session import (
    LoginAPIView,
    LogoutAPIView,
)

__all__ = [
    "ChangePasswordAPIView",
    "LoginAPIView",
    "LogoutAPIView",
    "PasswordResetConfirmAPIView",
    "PasswordResetRequestAPIView",
    "RegisterAPIView",
    "VerifyEmailAPIView",
]
