from __future__ import annotations

from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def authenticate_user(*, email: str, password: str, request=None):
    """Аутентифицирует пользователя по email и паролю."""

    email = (email or "").strip().lower()

    user = authenticate(
        request=request,
        email=email,
        password=password,
    )

    if not user:
        raise ValidationError({"detail": _("Неверная эл. почта или пароль.")})

    if not user.is_active:
        raise ValidationError({"detail": _("Учетная запись деактивирована.")})

    return user
