from __future__ import annotations

from collections.abc import Iterable
from datetime import date
from typing import Any

from django.db import transaction

from apps.schedule.constants import ScheduleStatus
from apps.schedule.models import SchedulePattern, SchedulePatternAudience

from .conflict_services import detect_conflicts_for_pattern

PATTERN_COPY_FIELDS = (
    "organization",
    "academic_year",
    "education_period",
    "week_template",
    "weekday",
    "time_slot",
    "starts_at",
    "ends_at",
    "group",
    "subject",
    "teacher",
    "room",
    "group_subject",
    "teacher_group_subject",
    "course",
    "course_lesson",
    "title",
    "lesson_type",
    "source_type",
    "status",
    "starts_on",
    "ends_on",
    "repeat_rule",
    "priority",
    "is_active",
    "notes",
)

PATTERN_AUDIENCE_COPY_FIELDS = (
    "audience_type",
    "group",
    "subgroup_name",
    "student",
    "course_enrollment",
    "notes",
)


def _sync_pattern_audiences(
    pattern: SchedulePattern,
    audiences: Iterable[dict[str, Any]] | None,
) -> None:
    if audiences is None:
        return

    pattern.audiences.all().delete()

    SchedulePatternAudience.objects.bulk_create(
        [
            SchedulePatternAudience(
                pattern=pattern,
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


def validate_pattern(pattern: SchedulePattern) -> list:
    pattern.full_clean()
    return detect_conflicts_for_pattern(pattern)


@transaction.atomic
def create_pattern(
    *,
    audiences: Iterable[dict[str, Any]] | None = None,
    validate_conflicts: bool = True,
    **data,
) -> SchedulePattern:
    pattern = SchedulePattern(**data)
    pattern.full_clean()
    pattern.save()

    _sync_pattern_audiences(pattern, audiences)

    if validate_conflicts:
        detect_conflicts_for_pattern(pattern)

    return pattern


@transaction.atomic
def update_pattern(
    pattern: SchedulePattern,
    *,
    audiences: Iterable[dict[str, Any]] | None = None,
    validate_conflicts: bool = True,
    **data,
) -> SchedulePattern:
    for field_name, value in data.items():
        setattr(pattern, field_name, value)

    pattern.full_clean()
    pattern.save()

    _sync_pattern_audiences(pattern, audiences)

    if validate_conflicts:
        detect_conflicts_for_pattern(pattern)

    return pattern


@transaction.atomic
def deactivate_pattern(pattern: SchedulePattern) -> SchedulePattern:
    pattern.is_active = False
    pattern.status = ScheduleStatus.ARCHIVED
    pattern.full_clean()
    pattern.save(update_fields=("is_active", "status", "updated_at"))
    return pattern


@transaction.atomic
def copy_patterns_to_period(
    *,
    patterns: Iterable[SchedulePattern],
    academic_year=None,
    education_period=None,
    starts_on: date | None = None,
    ends_on: date | None = None,
    week_template=None,
    copied_status: str = ScheduleStatus.DRAFT,
) -> list[SchedulePattern]:
    copied_patterns: list[SchedulePattern] = []

    for source_pattern in patterns:
        pattern_data = {
            field_name: getattr(source_pattern, field_name)
            for field_name in PATTERN_COPY_FIELDS
        }

        if academic_year is not None:
            pattern_data["academic_year"] = academic_year

        if education_period is not None:
            pattern_data["education_period"] = education_period

        if starts_on is not None:
            pattern_data["starts_on"] = starts_on

        if ends_on is not None:
            pattern_data["ends_on"] = ends_on

        if week_template is not None:
            pattern_data["week_template"] = week_template

        pattern_data["status"] = copied_status
        pattern_data["is_active"] = True

        copied_pattern = SchedulePattern(**pattern_data)
        copied_pattern.full_clean()
        copied_pattern.save()

        for source_audience in source_pattern.audiences.all():
            audience_data = {
                field_name: getattr(source_audience, field_name)
                for field_name in PATTERN_AUDIENCE_COPY_FIELDS
            }
            SchedulePatternAudience.objects.create(
                pattern=copied_pattern,
                **audience_data,
            )

        copied_patterns.append(copied_pattern)

    return copied_patterns
