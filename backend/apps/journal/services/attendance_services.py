from __future__ import annotations

import logging
from collections.abc import Iterable

from django.db import transaction

from apps.journal.models import AttendanceRecord, JournalLesson
from apps.journal.models.choices import AttendanceStatus

logger = logging.getLogger(__name__)


@transaction.atomic
def mark_attendance(
    *,
    lesson: JournalLesson,
    student,
    status: str,
    comment: str = "",
) -> AttendanceRecord:
    """Создаёт или обновляет посещаемость студента на занятии."""

    logger.info(
        "mark_attendance started lesson_id=%s student_id=%s status=%s",
        lesson.id,
        getattr(student, "id", None),
        status,
    )

    attendance, _ = AttendanceRecord.objects.update_or_create(
        lesson=lesson,
        student=student,
        defaults={
            "status": status,
            "comment": comment,
        },
    )

    attendance.full_clean()
    attendance.save()

    logger.info("mark_attendance completed attendance_id=%s", attendance.id)
    return attendance


@transaction.atomic
def mark_present(
    *,
    lesson: JournalLesson,
    student,
    comment: str = "",
) -> AttendanceRecord:
    """Отмечает студента присутствующим."""

    return mark_attendance(
        lesson=lesson,
        student=student,
        status=AttendanceStatus.PRESENT,
        comment=comment,
    )


@transaction.atomic
def mark_absent(
    *,
    lesson: JournalLesson,
    student,
    comment: str = "",
) -> AttendanceRecord:
    """Отмечает студента отсутствующим."""

    return mark_attendance(
        lesson=lesson,
        student=student,
        status=AttendanceStatus.ABSENT,
        comment=comment,
    )


@transaction.atomic
def mark_late(
    *,
    lesson: JournalLesson,
    student,
    comment: str = "",
) -> AttendanceRecord:
    """Отмечает опоздание студента."""

    return mark_attendance(
        lesson=lesson,
        student=student,
        status=AttendanceStatus.LATE,
        comment=comment,
    )


@transaction.atomic
def bulk_mark_attendance(
    *,
    lesson: JournalLesson,
    students: Iterable,
    status: str,
    comment: str = "",
) -> list[AttendanceRecord]:
    """Массово отмечает посещаемость студентов."""

    records: list[AttendanceRecord] = []

    for student in students:
        records.append(
            mark_attendance(
                lesson=lesson,
                student=student,
                status=status,
                comment=comment,
            )
        )

    return records


@transaction.atomic
def delete_attendance_record(attendance: AttendanceRecord) -> None:
    """Удаляет запись посещаемости."""

    logger.info("delete_attendance_record started attendance_id=%s", attendance.id)
    attendance.delete()
    logger.info("delete_attendance_record completed")
