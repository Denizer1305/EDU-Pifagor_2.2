from __future__ import annotations

from typing import Any

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_required_relation(
    value: Any,
    *,
    field_name: str,
    message: str | None = None,
) -> None:
    if value is None:
        raise ValidationError(
            {field_name: message or _("Обязательная связанная сущность не указана.")}
        )


def validate_active_object(
    obj: Any,
    *,
    field_name: str,
    message: str | None = None,
) -> None:
    if obj is None:
        return

    if getattr(obj, "is_active", True) is False:
        raise ValidationError(
            {field_name: message or _("Нельзя использовать неактивный объект.")}
        )


def validate_status_transition(
    current_status: str,
    target_status: str,
    *,
    allowed_transitions: dict[str, set[str]],
    field_name: str = "status",
) -> None:
    allowed_targets = allowed_transitions.get(current_status, set())

    if target_status not in allowed_targets:
        raise ValidationError(
            {
                field_name: _(
                    "Недопустимый переход статуса: %(current)s -> %(target)s."
                )
                % {
                    "current": current_status,
                    "target": target_status,
                }
            }
        )


def validate_positive_or_zero(
    value: int | None,
    *,
    field_name: str,
) -> None:
    if value is None:
        return

    if value < 0:
        raise ValidationError({field_name: _("Значение не может быть отрицательным.")})


def validate_positive(
    value: int | None,
    *,
    field_name: str,
) -> None:
    if value is None:
        return

    if value <= 0:
        raise ValidationError({field_name: _("Значение должно быть больше нуля.")})
