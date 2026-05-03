from __future__ import annotations

from .normalizers import _normalize_registration_data
from .profile_setup import (
    _configure_other_role_profile,
    _configure_student_profile,
    _configure_teacher_profile,
)
from .service import register_user
from .user_factory import _create_user_with_profile
from .validators import (
    _validate_registration_base,
    _validate_teacher_registration,
)

__all__ = [
    "_configure_other_role_profile",
    "_configure_student_profile",
    "_configure_teacher_profile",
    "_create_user_with_profile",
    "_normalize_registration_data",
    "_validate_registration_base",
    "_validate_teacher_registration",
    "register_user",
]
