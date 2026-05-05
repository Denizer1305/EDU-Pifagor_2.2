from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from django.db import transaction
from django.utils import timezone

from apps.schedule.constants import BatchStatus, GenerationSource
from apps.schedule.models import (
    ScheduledLesson,
    ScheduleGenerationBatch,
    SchedulePattern,
)
from apps.schedule.services.conflict_services import detect_conflicts_for_lesson


def _get_batch_status(name: str, fallback: str) -> str:
    return getattr(BatchStatus, name, fallback)


def _iter_dates(starts_on: date, ends_on: date):
    current = starts_on

    while current <= ends_on:
        yield current
        current += timedelta(days=1)


def _get_generation_period(
    *,
    batch: ScheduleGenerationBatch,
    starts_on: date | None = None,
    ends_on: date | None = None,
) -> tuple[date, date]:
    if starts_on and ends_on:
        return starts_on, ends_on

    if batch.education_period_id:
        period = batch.education_period
        return period.starts_on, period.ends_on

    raise ValueError("Нужно передать starts_on/ends_on или указать учебный период.")


def _create_lesson_from_pattern(
    *,
    pattern: SchedulePattern,
    lesson_date: date,
    dry_run: bool,
) -> ScheduledLesson | None:
    if dry_run:
        return None

    return ScheduledLesson.objects.create(
        organization=pattern.organization,
        academic_year=pattern.academic_year,
        education_period=pattern.education_period,
        pattern=pattern,
        date=lesson_date,
        weekday=lesson_date.isoweekday(),
        time_slot=pattern.time_slot,
        starts_at=pattern.starts_at,
        ends_at=pattern.ends_at,
        group=pattern.group,
        subject=pattern.subject,
        teacher=pattern.teacher,
        room=pattern.room,
        course=pattern.course,
        course_lesson=pattern.course_lesson,
        lesson_type=pattern.lesson_type,
        source_type=GenerationSource.PATTERNS,
    )


def _get_patterns_for_batch(
    *,
    batch: ScheduleGenerationBatch,
    starts_on: date,
    ends_on: date,
) -> Any:
    return (
        SchedulePattern.objects.select_related(
            "organization",
            "academic_year",
            "education_period",
            "time_slot",
            "group",
            "subject",
            "teacher",
            "room",
            "course",
            "course_lesson",
        )
        .filter(
            organization=batch.organization,
            academic_year=batch.academic_year,
            is_active=True,
            starts_on__lte=ends_on,
        )
        .filter(ends_on__isnull=True)
        | SchedulePattern.objects.select_related(
            "organization",
            "academic_year",
            "education_period",
            "time_slot",
            "group",
            "subject",
            "teacher",
            "room",
            "course",
            "course_lesson",
        ).filter(
            organization=batch.organization,
            academic_year=batch.academic_year,
            is_active=True,
            starts_on__lte=ends_on,
            ends_on__gte=starts_on,
        )
    ).distinct()


@transaction.atomic
def generate_lessons_from_patterns(
    *,
    batch: ScheduleGenerationBatch,
    starts_on: date | None = None,
    ends_on: date | None = None,
    detect_conflicts: bool = True,
) -> ScheduleGenerationBatch:
    starts_on, ends_on = _get_generation_period(
        batch=batch,
        starts_on=starts_on,
        ends_on=ends_on,
    )

    batch.status = _get_batch_status("RUNNING", "running")
    batch.started_at = timezone.now()
    batch.lessons_created = 0
    batch.lessons_updated = 0
    batch.conflicts_count = 0
    batch.log = ""
    batch.save(
        update_fields=(
            "status",
            "started_at",
            "lessons_created",
            "lessons_updated",
            "conflicts_count",
            "log",
            "updated_at",
        )
    )

    created_lessons: list[ScheduledLesson] = []
    log_lines: list[str] = []

    patterns = _get_patterns_for_batch(
        batch=batch,
        starts_on=starts_on,
        ends_on=ends_on,
    )

    for pattern in patterns:
        for lesson_date in _iter_dates(starts_on, ends_on):
            if lesson_date.isoweekday() != pattern.weekday:
                continue

            if lesson_date < pattern.starts_on:
                continue

            if pattern.ends_on and lesson_date > pattern.ends_on:
                continue

            exists = ScheduledLesson.objects.filter(
                pattern=pattern,
                date=lesson_date,
            ).exists()

            if exists:
                batch.lessons_updated += 1
                continue

            try:
                lesson = _create_lesson_from_pattern(
                    pattern=pattern,
                    lesson_date=lesson_date,
                    dry_run=batch.dry_run,
                )

                batch.lessons_created += 1

                if lesson is not None:
                    created_lessons.append(lesson)
            except Exception as exc:
                log_lines.append(f"Шаблон {pattern.id}, дата {lesson_date}: {exc}")

    if detect_conflicts and not batch.dry_run:
        for lesson in created_lessons:
            conflicts = detect_conflicts_for_lesson(lesson)
            batch.conflicts_count += len(conflicts)

    batch.status = (
        _get_batch_status("COMPLETED", "completed")
        if not log_lines
        else _get_batch_status("PARTIAL", "partial")
    )
    batch.finished_at = timezone.now()
    batch.log = "\n".join(log_lines)
    batch.save(
        update_fields=(
            "status",
            "finished_at",
            "lessons_created",
            "lessons_updated",
            "conflicts_count",
            "log",
            "updated_at",
        )
    )

    return batch


def generate_lessons_from_ktp(
    *,
    batch: ScheduleGenerationBatch,
    starts_on: date | None = None,
    ends_on: date | None = None,
    detect_conflicts: bool = True,
) -> ScheduleGenerationBatch:
    batch.source = GenerationSource.KTP
    batch.save(update_fields=("source", "updated_at"))

    return generate_lessons_from_patterns(
        batch=batch,
        starts_on=starts_on,
        ends_on=ends_on,
        detect_conflicts=detect_conflicts,
    )


def generate_lessons_from_course(
    *,
    batch: ScheduleGenerationBatch,
    starts_on: date | None = None,
    ends_on: date | None = None,
    detect_conflicts: bool = True,
) -> ScheduleGenerationBatch:
    batch.source = GenerationSource.COURSE
    batch.save(update_fields=("source", "updated_at"))

    return generate_lessons_from_patterns(
        batch=batch,
        starts_on=starts_on,
        ends_on=ends_on,
        detect_conflicts=detect_conflicts,
    )


def dry_run_generation(
    *,
    batch: ScheduleGenerationBatch,
    starts_on: date | None = None,
    ends_on: date | None = None,
) -> ScheduleGenerationBatch:
    batch.dry_run = True
    batch.save(update_fields=("dry_run", "updated_at"))

    return generate_lessons_from_patterns(
        batch=batch,
        starts_on=starts_on,
        ends_on=ends_on,
        detect_conflicts=True,
    )


def regenerate_period_schedule(
    *,
    batch: ScheduleGenerationBatch,
    starts_on: date | None = None,
    ends_on: date | None = None,
    delete_unlocked_existing: bool = False,
) -> ScheduleGenerationBatch:
    starts_on, ends_on = _get_generation_period(
        batch=batch,
        starts_on=starts_on,
        ends_on=ends_on,
    )

    if delete_unlocked_existing and not batch.dry_run:
        ScheduledLesson.objects.filter(
            organization=batch.organization,
            academic_year=batch.academic_year,
            date__gte=starts_on,
            date__lte=ends_on,
            is_locked=False,
        ).delete()

    return generate_lessons_from_patterns(
        batch=batch,
        starts_on=starts_on,
        ends_on=ends_on,
        detect_conflicts=True,
    )
