from __future__ import annotations

from typing import Any

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_room_same_organization(
    organization_id: int | None,
    room: Any,
    *,
    field_name: str = "room",
) -> None:
    if not organization_id or room is None:
        return

    if getattr(room, "organization_id", None) != organization_id:
        raise ValidationError(
            {field_name: _("Кабинет должен принадлежать выбранной организации.")}
        )


def validate_room_capacity_for_group(
    room: Any,
    group: Any,
    *,
    field_name: str = "room",
) -> None:
    if room is None or group is None:
        return

    room_capacity = getattr(room, "capacity", None)
    students_count = getattr(group, "students_count", None)

    if room_capacity is None or students_count is None:
        return

    if room_capacity < students_count:
        raise ValidationError(
            {
                field_name: _(
                    "Вместимость кабинета меньше количества студентов в группе."
                )
            }
        )
