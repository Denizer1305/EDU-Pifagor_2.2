from __future__ import annotations

from django.utils.translation import gettext_lazy as _

from apps.schedule.constants import ConflictSeverity, ConflictStatus, ConflictType
from apps.schedule.models import ScheduleConflict, SchedulePattern

from .common import (
    create_conflict,
    get_pattern_overlap_queryset,
    get_pattern_time_range,
    time_range_overlaps,
)


def _clear_pattern_conflicts(pattern: SchedulePattern) -> None:
    if pattern.pk:
        ScheduleConflict.objects.filter(
            pattern=pattern,
            status=ConflictStatus.OPEN,
        ).delete()


def detect_conflicts_for_pattern(
    pattern: SchedulePattern,
    *,
    clear_existing: bool = True,
) -> list[ScheduleConflict]:
    if clear_existing:
        _clear_pattern_conflicts(pattern)

    conflicts: list[ScheduleConflict] = []
    starts_at, ends_at = get_pattern_time_range(pattern)

    for related_pattern in get_pattern_overlap_queryset(pattern):
        related_starts_at, related_ends_at = get_pattern_time_range(related_pattern)

        if not time_range_overlaps(
            starts_at,
            ends_at,
            related_starts_at,
            related_ends_at,
        ):
            continue

        if pattern.teacher_id and pattern.teacher_id == related_pattern.teacher_id:
            conflicts.append(
                create_conflict(
                    organization=pattern.organization,
                    conflict_type=ConflictType.TEACHER_OVERLAP,
                    severity=ConflictSeverity.ERROR,
                    pattern=pattern,
                    related_pattern=related_pattern,
                    teacher=pattern.teacher,
                    starts_at=starts_at,
                    ends_at=ends_at,
                    message=_("В шаблоне преподаватель уже занят в это время."),
                )
            )

        if pattern.room_id and pattern.room_id == related_pattern.room_id:
            conflicts.append(
                create_conflict(
                    organization=pattern.organization,
                    conflict_type=ConflictType.ROOM_OVERLAP,
                    severity=ConflictSeverity.ERROR,
                    pattern=pattern,
                    related_pattern=related_pattern,
                    room=pattern.room,
                    starts_at=starts_at,
                    ends_at=ends_at,
                    message=_("В шаблоне аудитория уже занята в это время."),
                )
            )

        if pattern.group_id and pattern.group_id == related_pattern.group_id:
            conflicts.append(
                create_conflict(
                    organization=pattern.organization,
                    conflict_type=ConflictType.GROUP_OVERLAP,
                    severity=ConflictSeverity.ERROR,
                    pattern=pattern,
                    related_pattern=related_pattern,
                    group=pattern.group,
                    starts_at=starts_at,
                    ends_at=ends_at,
                    message=_("В шаблоне группа уже занята в это время."),
                )
            )

    return conflicts
