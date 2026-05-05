from __future__ import annotations

from apps.schedule.constants import ScheduleChangeType
from apps.schedule.models import ScheduleChange
from apps.schedule.tests.factories.course import create_user
from apps.schedule.tests.factories.lessons import (
    create_scheduled_lesson,
)


def _clean_kwargs(model_class, values: dict) -> dict:
    model_fields = {field.name for field in model_class._meta.fields}
    return {key: value for key, value in values.items() if key in model_fields}


def create_schedule_change(**kwargs):
    scheduled_lesson = (
        kwargs.pop("scheduled_lesson", None)
        or kwargs.pop("lesson", None)
        or create_scheduled_lesson()
    )

    old_time_slot = kwargs.pop("old_time_slot", None)
    new_time_slot = kwargs.pop("new_time_slot", None)

    defaults = {
        "scheduled_lesson": scheduled_lesson,
        "change_type": kwargs.pop(
            "change_type",
            ScheduleChangeType.RESCHEDULE,
        ),
        "old_date": kwargs.pop("old_date", scheduled_lesson.date),
        "new_date": kwargs.pop("new_date", scheduled_lesson.date),
        "old_time_slot": old_time_slot,
        "new_time_slot": new_time_slot,
        "old_starts_at": kwargs.pop("old_starts_at", scheduled_lesson.starts_at),
        "new_starts_at": kwargs.pop("new_starts_at", scheduled_lesson.starts_at),
        "old_ends_at": kwargs.pop("old_ends_at", scheduled_lesson.ends_at),
        "new_ends_at": kwargs.pop("new_ends_at", scheduled_lesson.ends_at),
        "old_room": kwargs.pop("old_room", scheduled_lesson.room),
        "new_room": kwargs.pop("new_room", scheduled_lesson.room),
        "old_teacher": kwargs.pop("old_teacher", scheduled_lesson.teacher),
        "new_teacher": kwargs.pop("new_teacher", scheduled_lesson.teacher),
        "reason": kwargs.pop("reason", "Тестовое изменение расписания"),
        "changed_by": kwargs.pop("changed_by", None),
        "comment": kwargs.pop("comment", ""),
    }

    if defaults["changed_by"] is None:
        defaults["changed_by"] = create_user()

    if defaults["old_time_slot"] is None:
        defaults["old_time_slot"] = scheduled_lesson.time_slot

    if defaults["new_time_slot"] is None:
        defaults["new_time_slot"] = scheduled_lesson.time_slot

    defaults.update(kwargs)

    return ScheduleChange.objects.create(**_clean_kwargs(ScheduleChange, defaults))
