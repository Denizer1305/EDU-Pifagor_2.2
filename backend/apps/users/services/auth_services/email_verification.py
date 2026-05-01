from __future__ import annotations

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import signing
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from apps.users.constants import (
    ONBOARDING_STATUS_DRAFT,
    ONBOARDING_STATUS_PENDING,
)
from apps.users.services.auth_services.constants import VERIFY_EMAIL_SALT
from apps.users.services.user_services import mark_user_email_verified

User = get_user_model()


def build_verify_email_token(user) -> str:
    """Создаёт токен подтверждения email."""

    payload = {
        "user_id": user.id,
        "email": user.email,
    }
    return signing.dumps(payload, salt=VERIFY_EMAIL_SALT)


def read_verify_email_token(token: str, max_age: int | None = None) -> dict:
    """Читает токен подтверждения email."""

    max_age = max_age or int(
        getattr(
            settings,
            "VERIFY_EMAIL_TOKEN_TTL",
            60 * 60 * 24,
        )
    )

    try:
        return signing.loads(
            token,
            salt=VERIFY_EMAIL_SALT,
            max_age=max_age,
        )
    except signing.SignatureExpired as exc:
        raise ValidationError({"token": _("Срок действия токена истёк.")}) from exc
    except signing.BadSignature as exc:
        raise ValidationError({"token": _("Некорректный токен.")}) from exc


def verify_user_email_by_token(token: str):
    """Подтверждает email пользователя по токену."""

    payload = read_verify_email_token(token)

    try:
        user = User.objects.get(
            id=payload["user_id"],
            email=payload["email"],
        )
    except User.DoesNotExist as exc:
        raise ValidationError(
            {"token": _("Пользователь по токену не найден.")}
        ) from exc

    mark_user_email_verified(user)

    if user.onboarding_status == ONBOARDING_STATUS_DRAFT:
        user.onboarding_status = ONBOARDING_STATUS_PENDING
        user.save(update_fields=["onboarding_status", "updated_at"])

    return user
