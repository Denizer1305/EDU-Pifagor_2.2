from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from apps.schedule.models import ScheduledLesson, ScheduledLessonAudience

LESSON_AUDIENCE_FIELDS = (
    "audience_type",
    "group",
    "subgroup_name",
    "student",
    "course_enrollment",
    "notes",
)


def sync_lesson_audiences(
    lesson: ScheduledLesson,
    audiences: Iterable[dict[str, Any]] | None,
) -> None:
    if audiences is None:
        return

    lesson.audiences.all().delete()

    ScheduledLessonAudience.objects.bulk_create(
        [
            ScheduledLessonAudience(
                scheduled_lesson=lesson,
                audience_type=audience.get("audience_type"),
                group=audience.get("group"),
                subgroup_name=audience.get("subgroup_name", ""),
                student=audience.get("student"),
                course_enrollment=audience.get("course_enrollment"),
                notes=audience.get("notes", ""),
            )
            for audience in audiences
        ]
    )
