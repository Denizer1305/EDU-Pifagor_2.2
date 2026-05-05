from __future__ import annotations

from typing import Any

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_object_same_organization(
    base_object: Any,
    related_object: Any,
    *,
    field_name: str,
    message: str | None = None,
) -> None:
    if base_object is None or related_object is None:
        return

    base_organization_id = getattr(base_object, "organization_id", None)
    related_organization_id = getattr(related_object, "organization_id", None)

    if (
        base_organization_id
        and related_organization_id
        and base_organization_id != related_organization_id
    ):
        raise ValidationError(
            {field_name: message or _("Объект должен принадлежать той же организации.")}
        )


def validate_group_same_organization(
    organization_id: int | None,
    group: Any,
    *,
    field_name: str = "group",
) -> None:
    if not organization_id or group is None:
        return

    if getattr(group, "organization_id", None) != organization_id:
        raise ValidationError(
            {field_name: _("Группа должна принадлежать выбранной организации.")}
        )


def validate_time_slot_same_organization(
    organization_id: int | None,
    time_slot: Any,
    *,
    field_name: str = "time_slot",
) -> None:
    if not organization_id or time_slot is None:
        return

    if getattr(time_slot, "organization_id", None) != organization_id:
        raise ValidationError(
            {field_name: _("Временной слот должен принадлежать выбранной организации.")}
        )
