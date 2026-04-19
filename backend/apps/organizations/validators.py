from __future__ import annotations

import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


GROUP_CODE_PATTERN = re.compile(r"^[A-Za-zА-Яа-я0-9\-_/ ]+$")
ACADEMIC_YEAR_PATTERN = re.compile(r"^\d{4}/\d{4}$")


def validate_group_code(value: str) -> None:
    """
    Проверяет код учебной группы.
    Разрешает буквы, цифры, дефис, подчёркивание, слэш и пробел.
    """
    if not value:
        raise ValidationError(_("Код группы обязателен."))

    value = value.strip()
    if not GROUP_CODE_PATTERN.fullmatch(value):
        raise ValidationError(
            _("Код группы содержит недопустимые символы.")
        )


def validate_academic_year(value: str) -> None:
    """
    Проверяет формат учебного года.
    Ожидаемый формат: YYYY/YYYY, например 2025/2026.
    """
    if not value:
        return

    value = value.strip()
    if not ACADEMIC_YEAR_PATTERN.fullmatch(value):
        raise ValidationError(
            _("Учебный год должен быть в формате ГГГГ/ГГГГ.")
        )

    start_year, end_year = value.split("/")
    if int(end_year) != int(start_year) + 1:
        raise ValidationError(
            _("Учебный год должен состоять из двух последовательных лет.")
        )


def validate_year_order(
    *,
    admission_year: int | None,
    graduation_year: int | None,
) -> None:
    """
    Проверяет, что год выпуска не раньше года набора.
    """
    if admission_year and graduation_year and graduation_year < admission_year:
        raise ValidationError(
            _("Год выпуска не может быть раньше года набора.")
        )


def validate_date_range(*, starts_at, ends_at) -> None:
    """
    Проверяет, что дата окончания не раньше даты начала.
    """
    if starts_at and ends_at and ends_at < starts_at:
        raise ValidationError(
            _("Дата окончания не может быть раньше даты начала.")
        )
