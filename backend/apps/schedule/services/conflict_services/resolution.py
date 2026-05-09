from __future__ import annotations

from django.db import transaction

from apps.schedule.constants import ConflictStatus
from apps.schedule.models import ScheduleConflict


@transaction.atomic
def resolve_conflict(
    conflict: ScheduleConflict,
    *,
    user=None,
    notes: str = "",
) -> ScheduleConflict:
    conflict.mark_resolved(user=user)

    if notes:
        conflict.notes = notes

    conflict.full_clean()
    conflict.save(
        update_fields=(
            "status",
            "resolved_by",
            "resolved_at",
            "notes",
            "updated_at",
        )
    )
    return conflict


@transaction.atomic
def ignore_conflict(
    conflict: ScheduleConflict,
    *,
    user=None,
    notes: str = "",
) -> ScheduleConflict:
    conflict.status = ConflictStatus.IGNORED
    conflict.resolved_by = user
    conflict.resolved_at = None

    if notes:
        conflict.notes = notes

    conflict.full_clean()
    conflict.save(
        update_fields=(
            "status",
            "resolved_by",
            "resolved_at",
            "notes",
            "updated_at",
        )
    )
    return conflict
