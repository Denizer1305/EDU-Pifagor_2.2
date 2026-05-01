from __future__ import annotations

from django.conf import settings
from django.contrib.auth import get_user_model, password_validation
from django.core import signing
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from apps.users.services.auth_services.constants import RESET_PASSWORD_SALT

User = get_user_model()


def build_password_reset_token(user) -> str:
    """Создаёт токен сброса пароля."""

    payload = {
        "user_id": user.id,
        "email": user.email,
    }
    return signing.dumps(payload, salt=RESET_PASSWORD_SALT)


def read_password_reset_token(token: str, max_age: int | None = None) -> dict:
    """Читает токен сброса пароля."""

    max_age = max_age or int(
        getattr(
            settings,
            "RESET_PASSWORD_TOKEN_TTL",
            60 * 60 * 3,
        )
    )

    try:
        return signing.loads(
            token,
            salt=RESET_PASSWORD_SALT,
            max_age=max_age,
        )
    except signing.SignatureExpired as exc:
        raise ValidationError({"token": _("Срок действия токена истёк.")}) from exc
    except signing.BadSignature as exc:
        raise ValidationError({"token": _("Некорректный токен.")}) from exc


def reset_password_by_token(
    *,
    token: str,
    password: str,
    password_repeat: str,
):
    """Сбрасывает пароль пользователя по токену."""

    if password != password_repeat:
        raise ValidationError({"password_repeat": _("Пароли не совпадают.")})

    payload = read_password_reset_token(token)

    try:
        user = User.objects.get(
            id=payload["user_id"],
            email=payload["email"],
            is_active=True,
        )
    except User.DoesNotExist as exc:
        raise ValidationError(
            {"token": _("Пользователь по токену не найден.")}
        ) from exc

    password_validation.validate_password(password, user=user)
    user.set_password(password)
    user.save(update_fields=["password", "updated_at"])
    return user
