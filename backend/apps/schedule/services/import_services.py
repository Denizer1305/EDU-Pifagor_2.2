from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, time
from typing import Any

from django.db import transaction
from django.utils import timezone

from apps.schedule.constants import BatchStatus
from apps.schedule.models import ScheduledLesson, ScheduleImportBatch
from apps.schedule.services.conflict_services import detect_conflicts_for_lesson


@dataclass(slots=True)
class ParsedScheduleRow:
    row_number: int
    data: dict[str, Any]
    errors: list[str] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return not self.errors


def _get_batch_status(name: str, fallback: str) -> str:
    return getattr(BatchStatus, name, fallback)


def _parse_date(value: Any) -> date | None:
    if isinstance(value, date):
        return value

    if not value:
        return None

    try:
        return date.fromisoformat(str(value))
    except ValueError:
        return None


def _parse_time(value: Any) -> time | None:
    if isinstance(value, time):
        return value

    if not value:
        return None

    try:
        return time.fromisoformat(str(value))
    except ValueError:
        return None


def parse_uploaded_schedule(
    *,
    rows: list[dict[str, Any]] | None = None,
    **_: Any,
) -> list[ParsedScheduleRow]:
    parsed_rows: list[ParsedScheduleRow] = []

    for index, row in enumerate(rows or [], start=1):
        errors: list[str] = []

        lesson_date = _parse_date(row.get("date"))
        starts_at = _parse_time(row.get("starts_at"))
        ends_at = _parse_time(row.get("ends_at"))

        if lesson_date is None:
            errors.append("Некорректная или пустая дата занятия.")

        if starts_at is None:
            errors.append("Некорректное или пустое время начала.")

        if ends_at is None:
            errors.append("Некорректное или пустое время окончания.")

        if starts_at and ends_at and ends_at <= starts_at:
            errors.append("Время окончания должно быть позже времени начала.")

        parsed_rows.append(
            ParsedScheduleRow(
                row_number=index,
                data={
                    **row,
                    "date": lesson_date,
                    "starts_at": starts_at,
                    "ends_at": ends_at,
                },
                errors=errors,
            )
        )

    return parsed_rows


def validate_import_rows(rows: list[ParsedScheduleRow]) -> None:
    invalid_rows = [row for row in rows if not row.is_valid]

    if invalid_rows:
        errors = [
            f"Строка {row.row_number}: {'; '.join(row.errors)}" for row in invalid_rows
        ]
        raise ValueError("\n".join(errors))


def _create_lesson_from_row(
    *,
    batch: ScheduleImportBatch,
    row: ParsedScheduleRow,
    created_by=None,
) -> ScheduledLesson:
    data = row.data

    return ScheduledLesson.objects.create(
        organization=batch.organization,
        academic_year=batch.academic_year,
        education_period=batch.education_period,
        date=data["date"],
        weekday=data["date"].isoweekday(),
        time_slot=data.get("time_slot"),
        starts_at=data["starts_at"],
        ends_at=data["ends_at"],
        group=data.get("group"),
        subject=data.get("subject"),
        teacher=data.get("teacher"),
        room=data.get("room"),
        course=data.get("course"),
        course_lesson=data.get("course_lesson"),
        lesson_type=data.get("lesson_type", ""),
        source_type=data.get("source_type", ""),
    )


@transaction.atomic
def apply_import_batch(
    *,
    batch: ScheduleImportBatch,
    rows: list[ParsedScheduleRow],
    created_by=None,
    validate_conflicts: bool = True,
) -> ScheduleImportBatch:
    batch.status = _get_batch_status("RUNNING", "running")
    batch.started_at = timezone.now()
    batch.rows_total = len(rows)
    batch.rows_success = 0
    batch.rows_failed = 0
    batch.log = ""
    batch.save(
        update_fields=(
            "status",
            "started_at",
            "rows_total",
            "rows_success",
            "rows_failed",
            "log",
            "updated_at",
        )
    )

    created_lessons: list[ScheduledLesson] = []
    log_lines: list[str] = []

    for row in rows:
        if not row.is_valid:
            batch.rows_failed += 1
            log_lines.append(f"Строка {row.row_number}: {'; '.join(row.errors)}")
            continue

        try:
            lesson = _create_lesson_from_row(
                batch=batch,
                row=row,
                created_by=created_by,
            )
            created_lessons.append(lesson)
            batch.rows_success += 1
        except Exception as exc:
            batch.rows_failed += 1
            log_lines.append(f"Строка {row.row_number}: {exc}")

    if validate_conflicts:
        for lesson in created_lessons:
            detect_conflicts_for_lesson(lesson)

    batch.status = (
        _get_batch_status("COMPLETED", "completed")
        if batch.rows_failed == 0
        else _get_batch_status("PARTIAL", "partial")
    )
    batch.finished_at = timezone.now()
    batch.log = "\n".join(log_lines)
    batch.save(
        update_fields=(
            "status",
            "finished_at",
            "rows_success",
            "rows_failed",
            "log",
            "updated_at",
        )
    )

    return batch


@transaction.atomic
def import_schedule_from_table(
    *,
    batch: ScheduleImportBatch,
    rows: list[dict[str, Any]],
    created_by=None,
    validate_conflicts: bool = True,
) -> ScheduleImportBatch:
    parsed_rows = parse_uploaded_schedule(rows=rows)

    return apply_import_batch(
        batch=batch,
        rows=parsed_rows,
        created_by=created_by,
        validate_conflicts=validate_conflicts,
    )
