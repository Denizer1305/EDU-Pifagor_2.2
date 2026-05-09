from __future__ import annotations

from datetime import date, time

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_date_range(
    starts_on: date | None,
    ends_on: date | None,
    *,
    ends_field: str = "ends_on",
) -> None:
    if starts_on and ends_on and ends_on < starts_on:
        raise ValidationError(
            {ends_field: _("Дата окончания не может быть раньше даты начала.")}
        )


def validate_time_range(
    starts_at: time | None,
    ends_at: time | None,
    *,
    ends_field: str = "ends_at",
) -> None:
    if starts_at and ends_at and ends_at <= starts_at:
        raise ValidationError(
            {ends_field: _("Время окончания должно быть позже времени начала.")}
        )


def validate_weekday(value: int | None, *, field_name: str = "weekday") -> None:
    if value is None:
        return

    if value < 1 or value > 7:
        raise ValidationError(
            {field_name: _("День недели должен быть числом от 1 до 7.")}
        )
