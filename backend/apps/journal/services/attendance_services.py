from __future__ import annotations

from collections.abc import Sequence

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from apps.journal.models import (
    AttendanceRecord,
    AttendanceStatus,
    JournalLesson,
)


def create_attendance_record(
    *,
    lesson: JournalLesson,
    student_id: int,
    status: str = AttendanceStatus.PRESENT,
    comment: str = "",
) -> AttendanceRecord:
    """
    Создаёт запись о посещаемости студента на занятии.
    Если запись уже существует — вызывает ValidationError.
    """
    if AttendanceRecord.objects.filter(lesson=lesson, student_id=student_id).exists():
        raise ValidationError(
            _(
                "Запись посещаемости для этого студента на данном занятии уже существует."
            )
        )

    record = AttendanceRecord(
        lesson=lesson,
        student_id=student_id,
        status=status,
        comment=comment,
    )
    record.full_clean()
    record.save()
    return record


def bulk_set_attendance(
    *,
    lesson: JournalLesson,
    records: Sequence[dict],
) -> list[AttendanceRecord]:
    """
    Массовое проставление посещаемости для занятия.

    Формат records:
        [
            {"student_id": 1, "status": "present", "comment": ""},
            {"student_id": 2, "status": "absent", "comment": "Болеет"},
        ]

    Логика:
    - Если запись уже есть — обновляет статус и комментарий.
    - Если нет — создаёт новую.
    - Всё выполняется в одной транзакции.
    """
    if not records:
        return []

    student_ids = [r["student_id"] for r in records]

    # Загружаем существующие записи одним запросом
    existing = {
        rec.student_id: rec
        for rec in AttendanceRecord.objects.filter(
            lesson=lesson, student_id__in=student_ids
        )
    }

    to_create: list[AttendanceRecord] = []
    to_update: list[AttendanceRecord] = []

    for item in records:
        student_id = item["student_id"]
        status = item.get("status", AttendanceStatus.PRESENT)
        comment = item.get("comment", "")

        if student_id in existing:
            rec = existing[student_id]
            rec.status = status
            rec.comment = comment
            to_update.append(rec)
        else:
            to_create.append(
                AttendanceRecord(
                    lesson=lesson,
                    student_id=student_id,
                    status=status,
                    comment=comment,
                )
            )

    with transaction.atomic():
        if to_create:
            AttendanceRecord.objects.bulk_create(to_create)
        if to_update:
            AttendanceRecord.objects.bulk_update(
                to_update, fields=["status", "comment", "updated_at"]
            )

    return to_create + to_update


def update_attendance_record(
    *,
    record: AttendanceRecord,
    status: str | None = None,
    comment: str | None = None,
) -> AttendanceRecord:
    """
    Обновляет статус и/или комментарий записи посещаемости.
    """
    update_fields = ["updated_at"]

    if status is not None:
        record.status = status
        update_fields.append("status")

    if comment is not None:
        record.comment = comment
        update_fields.append("comment")

    record.full_clean()
    record.save(update_fields=update_fields)
    return record
