from __future__ import annotations

from apps.schedule.constants import RoomType
from apps.schedule.models import ScheduleRoom
from apps.schedule.tests.factories._utils import next_number
from apps.schedule.tests.factories.course import create_organization


def _clean_kwargs(model_class, values: dict) -> dict:
    model_fields = {field.name for field in model_class._meta.fields}
    return {key: value for key, value in values.items() if key in model_fields}


def create_schedule_room(**kwargs):
    number = next_number("schedule_room")
    organization = kwargs.pop("organization", None) or create_organization()

    provided_name = kwargs.pop("name", None)
    provided_number = kwargs.pop("number", None)

    room_number = provided_number or provided_name or str(number)
    room_name = provided_name or f"Кабинет {room_number}"

    defaults = {
        "organization": organization,
        "name": room_name,
        "number": str(room_number),
        "building": kwargs.pop("building", "Главный корпус"),
        "floor": kwargs.pop("floor", 1),
        "capacity": kwargs.pop("capacity", 30),
        "room_type": kwargs.pop("room_type", RoomType.CLASSROOM),
        "is_active": kwargs.pop("is_active", True),
        "department": kwargs.pop("department", None),
        "notes": kwargs.pop("notes", ""),
    }
    defaults.update(kwargs)

    return ScheduleRoom.objects.create(**_clean_kwargs(ScheduleRoom, defaults))
