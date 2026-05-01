from __future__ import annotations

from .login import LoginSerializer
from .password import (
    ChangePasswordSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetSerializer,
)
from .registration import (
    BaseRegistrationSerializer,
    ParentRegistrationSerializer,
    StudentRegistrationSerializer,
    TeacherRegistrationSerializer,
)

__all__ = [
    "LoginSerializer",
    "BaseRegistrationSerializer",
    "StudentRegistrationSerializer",
    "ParentRegistrationSerializer",
    "TeacherRegistrationSerializer",
    "PasswordResetSerializer",
    "PasswordResetConfirmSerializer",
    "ChangePasswordSerializer",
]
