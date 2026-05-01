from __future__ import annotations

from django.contrib.auth.hashers import check_password
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


def _verify_teacher_registration_code(organization, code: str) -> None:
    """Проверяет код регистрации преподавателя.

    Работает в мягком режиме: если поля кодов ещё не добавлены в Organization,
    функция не ломает регистрацию.
    """

    code = (code or "").strip()
    if not code:
        raise ValidationError(
            {
                "teacher_registration_code": _(
                    "Необходимо указать код регистрации преподавателя."
                )
            }
        )

    has_hash = hasattr(organization, "teacher_registration_code_hash")
    has_active = hasattr(organization, "teacher_registration_code_is_active")
    has_expires = hasattr(organization, "teacher_registration_code_expires_at")

    if not has_hash:
        return

    code_hash = getattr(organization, "teacher_registration_code_hash", "") or ""
    if not code_hash:
        raise ValidationError(
            {
                "teacher_registration_code": _(
                    "Для организации не настроен код регистрации преподавателя."
                )
            }
        )

    if has_active and not getattr(
        organization,
        "teacher_registration_code_is_active",
        False,
    ):
        raise ValidationError(
            {
                "teacher_registration_code": _(
                    "Код регистрации преподавателя для организации отключён."
                )
            }
        )

    if has_expires:
        expires_at = getattr(
            organization,
            "teacher_registration_code_expires_at",
            None,
        )
        if expires_at and timezone.now() > expires_at:
            raise ValidationError(
                {
                    "teacher_registration_code": _(
                        "Срок действия кода регистрации преподавателя истёк."
                    )
                }
            )

    if not check_password(code, code_hash):
        raise ValidationError(
            {
                "teacher_registration_code": _(
                    "Неверный код регистрации преподавателя."
                )
            }
        )
