import re

from django.forms import ValidationError
from django.utils.translation import gettext_lazy as _

PHONE_PATTERN = re.compile(r"^[0-9+\-() ]+$")


def validate_phone(value: str) -> None:
    if not value:
        return

    if not PHONE_PATTERN.match(value):
        raise ValidationError(
            _("Номер телефона содержит недопустимые символы.")
        )

    digits_count = len(re.sub(r'\D', '', value))
    if digits_count < 6:
        raise ValidationError(
            _("Телефон слишком короткий.")
        )
    if digits_count > 20:
        raise ValidationError(
            _("Телефон слишком длинный.")
        )


def validate_email(email: str | None, reset_email: str | None) -> None:
    if not email and not reset_email:
        return

    if email and reset_email and email.strip().lower() == reset_email.strip().lower():
        raise ValidationError(
            _("Резервная почта не может совпадать с основной.")
        )
