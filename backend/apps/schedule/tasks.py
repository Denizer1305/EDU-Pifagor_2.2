from __future__ import annotations

from datetime import date
from typing import Any

from celery import shared_task
from django.utils.dateparse import parse_date

from apps.organizations.models import Organization
from apps.schedule.models import (
    ScheduledLesson,
    ScheduleGenerationBatch,
    ScheduleImportBatch,
)
from apps.schedule.services.conflict_services import detect_conflicts_for_period
from apps.schedule.services.generation_services import (
    dry_run_generation,
    generate_lessons_from_course,
    generate_lessons_from_ktp,
    generate_lessons_from_patterns,
    regenerate_period_schedule,
)
from apps.schedule.services.import_services import (
    apply_import_batch,
    parse_uploaded_schedule,
)
from apps.schedule.services.journal_sync_services import sync_schedule_to_journal


def _parse_task_date(value: str | date | None) -> date | None:
    if value is None:
        return None

    if isinstance(value, date):
        return value

    return parse_date(value)


def _parse_required_task_date(value: str | date, *, field_name: str) -> date:
    parsed = _parse_task_date(value)

    if parsed is None:
        raise ValueError(f"Некорректная дата в поле {field_name}.")

    return parsed


@shared_task(name="schedule.generate_lessons_from_patterns")
def generate_lessons_from_patterns_task(
    *,
    batch_id: int,
    starts_on: str | None = None,
    ends_on: str | None = None,
    detect_conflicts: bool = True,
) -> int:
    batch = ScheduleGenerationBatch.objects.get(pk=batch_id)

    generate_lessons_from_patterns(
        batch=batch,
        starts_on=_parse_task_date(starts_on),
        ends_on=_parse_task_date(ends_on),
        detect_conflicts=detect_conflicts,
    )

    return batch.id


@shared_task(name="schedule.generate_lessons_from_ktp")
def generate_lessons_from_ktp_task(
    *,
    batch_id: int,
    starts_on: str | None = None,
    ends_on: str | None = None,
    detect_conflicts: bool = True,
) -> int:
    batch = ScheduleGenerationBatch.objects.get(pk=batch_id)

    generate_lessons_from_ktp(
        batch=batch,
        starts_on=_parse_task_date(starts_on),
        ends_on=_parse_task_date(ends_on),
        detect_conflicts=detect_conflicts,
    )

    return batch.id


@shared_task(name="schedule.generate_lessons_from_course")
def generate_lessons_from_course_task(
    *,
    batch_id: int,
    starts_on: str | None = None,
    ends_on: str | None = None,
    detect_conflicts: bool = True,
) -> int:
    batch = ScheduleGenerationBatch.objects.get(pk=batch_id)

    generate_lessons_from_course(
        batch=batch,
        starts_on=_parse_task_date(starts_on),
        ends_on=_parse_task_date(ends_on),
        detect_conflicts=detect_conflicts,
    )

    return batch.id


@shared_task(name="schedule.dry_run_generation")
def dry_run_generation_task(
    *,
    batch_id: int,
    starts_on: str | None = None,
    ends_on: str | None = None,
) -> int:
    batch = ScheduleGenerationBatch.objects.get(pk=batch_id)

    dry_run_generation(
        batch=batch,
        starts_on=_parse_task_date(starts_on),
        ends_on=_parse_task_date(ends_on),
    )

    return batch.id


@shared_task(name="schedule.regenerate_period_schedule")
def regenerate_period_schedule_task(
    *,
    batch_id: int,
    starts_on: str | None = None,
    ends_on: str | None = None,
    delete_unlocked_existing: bool = False,
) -> int:
    batch = ScheduleGenerationBatch.objects.get(pk=batch_id)

    regenerate_period_schedule(
        batch=batch,
        starts_on=_parse_task_date(starts_on),
        ends_on=_parse_task_date(ends_on),
        delete_unlocked_existing=delete_unlocked_existing,
    )

    return batch.id


@shared_task(name="schedule.apply_import_batch")
def apply_import_batch_task(
    *,
    batch_id: int,
    rows: list[dict[str, Any]],
    validate_conflicts: bool = True,
) -> int:
    batch = ScheduleImportBatch.objects.get(pk=batch_id)
    parsed_rows = parse_uploaded_schedule(rows=rows)

    apply_import_batch(
        batch=batch,
        rows=parsed_rows,
        validate_conflicts=validate_conflicts,
    )

    return batch.id


@shared_task(name="schedule.sync_schedule_to_journal")
def sync_schedule_to_journal_task(*, lesson_id: int) -> dict[str, Any]:
    lesson = (
        ScheduledLesson.objects.select_related(
            "course",
            "course_lesson",
            "teacher",
            "time_slot",
        )
        .prefetch_related("audiences")
        .get(pk=lesson_id)
    )

    journal_lesson = sync_schedule_to_journal(lesson=lesson)

    return {
        "journal_lesson_id": journal_lesson.id,
        "lesson_id": lesson.id,
        "status": journal_lesson.status,
    }


@shared_task(name="schedule.detect_conflicts_for_period")
def detect_conflicts_for_period_task(
    *,
    organization_id: int,
    starts_on: str,
    ends_on: str,
) -> int:
    organization = Organization.objects.get(pk=organization_id)

    conflicts = detect_conflicts_for_period(
        organization=organization,
        starts_on=_parse_required_task_date(starts_on, field_name="starts_on"),
        ends_on=_parse_required_task_date(ends_on, field_name="ends_on"),
    )

    return len(conflicts)
