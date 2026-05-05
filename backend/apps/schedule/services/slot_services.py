from __future__ import annotations

from datetime import time

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from apps.schedule.constants import EducationLevel
from apps.schedule.models import ScheduleTimeSlot


def _normalize_slot_text(value: str | None) -> str:
    return (value or "").strip()


def _calculate_duration_minutes(*, starts_at: time, ends_at: time) -> int:
    start_minutes = starts_at.hour * 60 + starts_at.minute
    end_minutes = ends_at.hour * 60 + ends_at.minute
    return end_minutes - start_minutes


def validate_slot_time(*, starts_at: time, ends_at: time) -> None:
    """
    Проверяет корректность времени слота.
    """
    if ends_at <= starts_at:
        raise ValidationError(
            {"ends_at": _("Время окончания должно быть позже времени начала.")}
        )


@transaction.atomic
def create_time_slot(
    *,
    organization,
    name: str,
    number: int,
    starts_at: time,
    ends_at: time,
    education_level: str = EducationLevel.MIXED,
    is_pair: bool = False,
    duration_minutes: int | None = None,
    notes: str = "",
    is_active: bool = True,
) -> ScheduleTimeSlot:
    """
    Создаёт временной слот расписания.

    Для школы это может быть урок, для СПО — пара.
    """
    validate_slot_time(starts_at=starts_at, ends_at=ends_at)

    slot = ScheduleTimeSlot(
        organization=organization,
        name=_normalize_slot_text(name),
        number=number,
        starts_at=starts_at,
        ends_at=ends_at,
        duration_minutes=duration_minutes
        if duration_minutes is not None
        else _calculate_duration_minutes(starts_at=starts_at, ends_at=ends_at),
        education_level=education_level,
        is_pair=is_pair,
        notes=_normalize_slot_text(notes),
        is_active=is_active,
    )

    slot.full_clean()
    slot.save()

    return slot


@transaction.atomic
def update_time_slot(
    *,
    slot: ScheduleTimeSlot,
    name: str | None = None,
    number: int | None = None,
    starts_at: time | None = None,
    ends_at: time | None = None,
    duration_minutes: int | None = None,
    education_level: str | None = None,
    is_pair: bool | None = None,
    notes: str | None = None,
    is_active: bool | None = None,
) -> ScheduleTimeSlot:
    """
    Обновляет временной слот расписания.
    """
    new_starts_at = starts_at or slot.starts_at
    new_ends_at = ends_at or slot.ends_at

    validate_slot_time(starts_at=new_starts_at, ends_at=new_ends_at)

    if name is not None:
        slot.name = _normalize_slot_text(name)

    if number is not None:
        slot.number = number

    if starts_at is not None:
        slot.starts_at = starts_at

    if ends_at is not None:
        slot.ends_at = ends_at

    if duration_minutes is not None:
        slot.duration_minutes = duration_minutes
    elif starts_at is not None or ends_at is not None:
        slot.duration_minutes = _calculate_duration_minutes(
            starts_at=slot.starts_at,
            ends_at=slot.ends_at,
        )

    if education_level is not None:
        slot.education_level = education_level

    if is_pair is not None:
        slot.is_pair = is_pair

    if notes is not None:
        slot.notes = _normalize_slot_text(notes)

    if is_active is not None:
        slot.is_active = is_active

    slot.full_clean()
    slot.save()

    return slot


@transaction.atomic
def bulk_create_default_slots(
    *,
    organization,
    slots_data: list[dict],
    education_level: str = EducationLevel.MIXED,
    is_pair: bool = False,
) -> list[ScheduleTimeSlot]:
    """
    Массово создаёт типовые слоты.

    slots_data ожидается в формате:
    [
        {
            "name": "1 пара",
            "number": 1,
            "starts_at": time(8, 30),
            "ends_at": time(10, 0),
        },
        ...
    ]
    """
    created_slots: list[ScheduleTimeSlot] = []

    for slot_data in slots_data:
        created_slots.append(
            create_time_slot(
                organization=organization,
                name=slot_data["name"],
                number=slot_data["number"],
                starts_at=slot_data["starts_at"],
                ends_at=slot_data["ends_at"],
                duration_minutes=slot_data.get("duration_minutes"),
                education_level=slot_data.get("education_level", education_level),
                is_pair=slot_data.get("is_pair", is_pair),
                notes=slot_data.get("notes", ""),
                is_active=slot_data.get("is_active", True),
            )
        )

    return created_slots
