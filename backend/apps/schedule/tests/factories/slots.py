from __future__ import annotations

from datetime import time
from typing import Any

from apps.organizations.models import Organization
from apps.schedule.constants import EducationLevel
from apps.schedule.models import ScheduleTimeSlot
from apps.schedule.tests.factories.context import next_number
from apps.schedule.tests.factories.course import create_organization


def create_schedule_time_slot(
    *,
    organization: Organization | None = None,
    name: str | None = None,
    number: int | None = None,
    starts_at: time = time(9, 0),
    ends_at: time = time(9, 45),
    duration_minutes: int = 45,
    education_level: str = EducationLevel.MIXED,
    is_pair: bool = False,
    is_active: bool = True,
    **extra_fields: Any,
) -> ScheduleTimeSlot:
    slot_number = number or next_number()
    organization = organization or create_organization()

    return ScheduleTimeSlot.objects.create(
        organization=organization,
        name=name or f"{slot_number} занятие",
        number=slot_number,
        starts_at=starts_at,
        ends_at=ends_at,
        duration_minutes=duration_minutes,
        education_level=education_level,
        is_pair=is_pair,
        is_active=is_active,
        **extra_fields,
    )
