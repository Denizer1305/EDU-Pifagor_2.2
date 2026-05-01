from __future__ import annotations

from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def change_user_password(
    *,
    user,
    old_password: str,
    new_password: str,
    new_password_confirm: str,
):
    """Меняет пароль авторизованного пользователя."""

    if not user.check_password(old_password):
        raise ValidationError({"old_password": _("Текущий пароль указан неверно.")})

    if new_password != new_password_confirm:
        raise ValidationError({"new_password_confirm": _("Пароли не совпадают.")})

    if old_password == new_password:
        raise ValidationError(
            {"new_password": _("Новый пароль не может совпадать с текущим.")}
        )

    password_validation.validate_password(new_password, user=user)
    user.set_password(new_password)
    user.save(update_fields=["password", "updated_at"])
    return user
