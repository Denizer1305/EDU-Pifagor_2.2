from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from apps.schedule.constants import RoomType
from apps.schedule.models import ScheduleRoom


def _normalize_room_text(value: str | None) -> str:
    return (value or "").strip()


@transaction.atomic
def create_room(
    *,
    organization,
    name: str,
    department=None,
    number: str = "",
    room_type: str = RoomType.CLASSROOM,
    capacity: int = 0,
    floor: str = "",
    building: str = "",
    notes: str = "",
    is_active: bool = True,
) -> ScheduleRoom:
    """
    Создаёт аудиторию расписания.

    Используется для ручного заведения кабинетов, лабораторий,
    мастерских, спортзалов и онлайн-аудиторий.
    """
    room = ScheduleRoom(
        organization=organization,
        department=department,
        name=_normalize_room_text(name),
        number=_normalize_room_text(number),
        room_type=room_type,
        capacity=capacity,
        floor=_normalize_room_text(floor),
        building=_normalize_room_text(building),
        notes=_normalize_room_text(notes),
        is_active=is_active,
    )

    room.full_clean()
    room.save()

    return room


@transaction.atomic
def update_room(
    *,
    room: ScheduleRoom,
    name: str | None = None,
    department=...,
    number: str | None = None,
    room_type: str | None = None,
    capacity: int | None = None,
    floor: str | None = None,
    building: str | None = None,
    notes: str | None = None,
    is_active: bool | None = None,
) -> ScheduleRoom:
    """
    Обновляет аудиторию расписания.

    Значение department=... означает «не менять поле».
    department=None означает «очистить отделение».
    """
    if name is not None:
        room.name = _normalize_room_text(name)

    if department is not ...:
        room.department = department

    if number is not None:
        room.number = _normalize_room_text(number)

    if room_type is not None:
        room.room_type = room_type

    if capacity is not None:
        room.capacity = capacity

    if floor is not None:
        room.floor = _normalize_room_text(floor)

    if building is not None:
        room.building = _normalize_room_text(building)

    if notes is not None:
        room.notes = _normalize_room_text(notes)

    if is_active is not None:
        room.is_active = is_active

    room.full_clean()
    room.save()

    return room


@transaction.atomic
def archive_room(*, room: ScheduleRoom) -> ScheduleRoom:
    """
    Архивирует аудиторию.

    Физически аудитория не удаляется, потому что она может быть связана
    с уже созданным расписанием, историей замен и конфликтами.
    """
    if not room.is_active:
        raise ValidationError({"is_active": _("Аудитория уже находится в архиве.")})

    room.is_active = False
    room.full_clean()
    room.save(update_fields=("is_active", "updated_at"))

    return room
