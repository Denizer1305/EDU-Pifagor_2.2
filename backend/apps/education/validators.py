from __future__ import annotations

import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

ACADEMIC_YEAR_PATTERN = re.compile(r"^\d{4}/\d{4}$")
PERIOD_CODE_PATTERN = re.compile(r"^[A-Za-zА-Яа-я0-9\-_]+$")


def validate_academic_year_name(value: str) -> None:
    """
    Проверяет формат учебного года.
    Ожидаемый формат: YYYY/YYYY.
    """
    if not value:
        raise ValidationError(_("Наименование учебного года обязательно."))

    value = value.strip()
    if not ACADEMIC_YEAR_PATTERN.fullmatch(value):
        raise ValidationError(_("Учебный год должен быть в формате ГГГГ/ГГГГ."))

    start_year, end_year = value.split("/")
    if int(end_year) != int(start_year) + 1:
        raise ValidationError(
            _("Учебный год должен состоять из двух последовательных лет.")
        )


def validate_period_code(value: str) -> None:
    """
    Проверяет код учебного периода.
    """
    if not value:
        raise ValidationError(_("Код учебного периода обязателен."))

    value = value.strip()
    if not PERIOD_CODE_PATTERN.fullmatch(value):
        raise ValidationError(_("Код учебного периода содержит недопустимые символы."))


def validate_date_range(*, start_date, end_date) -> None:
    """
    Проверяет, что дата окончания позже даты начала.
    """
    if start_date and end_date and end_date <= start_date:
        raise ValidationError(_("Дата окончания должна быть позже даты начала."))


def validate_optional_date_range(*, starts_at, ends_at) -> None:
    """
    Проверяет, что дата окончания не раньше даты начала.
    """
    if starts_at and ends_at and ends_at < starts_at:
        raise ValidationError(_("Дата окончания не может быть раньше даты начала."))


def validate_hours_distribution(
    *,
    planned_hours: int,
    contact_hours: int,
    independent_hours: int,
) -> None:
    """
    Проверяет распределение часов.
    """
    if planned_hours < 0 or contact_hours < 0 or independent_hours < 0:
        raise ValidationError(_("Количество часов не может быть отрицательным."))

    if contact_hours > planned_hours:
        raise ValidationError(_("Контактные часы не могут превышать плановые часы."))

    if independent_hours > planned_hours:
        raise ValidationError(
            _("Самостоятельные часы не могут превышать плановые часы.")
        )


def validate_year_inside_academic_year(
    *,
    academic_year,
    date_value,
    field_name: str,
) -> None:
    """
    Проверяет, что дата входит в диапазон учебного года.
    """
    if not date_value:
        return

    if date_value < academic_year.start_date:
        raise ValidationError(
            {field_name: _("Дата не может быть раньше начала учебного года.")}
        )

    if date_value > academic_year.end_date:
        raise ValidationError(
            {field_name: _("Дата не может быть позже окончания учебного года.")}
        )
