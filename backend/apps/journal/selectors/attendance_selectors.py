from __future__ import annotations

from datetime import date
from typing import Any

from django.db.models import QuerySet
from django.shortcuts import get_object_or_404

from apps.journal.models import AttendanceRecord
from apps.journal.models.choices import AttendanceStatus


def get_attendance_queryset(
    *,
    lesson: Any | None = None,
    student: Any | None = None,
    course: Any | None = None,
    group: Any | None = None,
    status: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
) -> QuerySet[AttendanceRecord]:
    """Возвращает queryset записей посещаемости с фильтрами."""

    queryset = (
        AttendanceRecord.objects.select_related(
            "lesson",
            "lesson__course",
            "lesson__group",
            "student",
        )
        .all()
        .order_by("-lesson__date", "lesson__lesson_number", "student_id")
    )

    if lesson is not None:
        queryset = queryset.filter(lesson=lesson)

    if student is not None:
        queryset = queryset.filter(student=student)

    if course is not None:
        queryset = queryset.filter(lesson__course=course)

    if group is not None:
        queryset = queryset.filter(lesson__group=group)

    if status:
        queryset = queryset.filter(status=status)

    if date_from is not None:
        queryset = queryset.filter(lesson__date__gte=date_from)

    if date_to is not None:
        queryset = queryset.filter(lesson__date__lte=date_to)

    return queryset


def get_attendance_record_by_id(attendance_id: int) -> AttendanceRecord:
    """Возвращает запись посещаемости по id или 404."""

    return get_object_or_404(
        get_attendance_queryset(),
        id=attendance_id,
    )


def get_attendance_record(
    *,
    lesson: Any,
    student: Any,
) -> AttendanceRecord | None:
    """Возвращает запись посещаемости студента на конкретном занятии."""

    return get_attendance_queryset(
        lesson=lesson,
        student=student,
    ).first()


def get_lesson_attendance(lesson: Any) -> QuerySet[AttendanceRecord]:
    """Возвращает посещаемость по занятию."""

    return get_attendance_queryset(lesson=lesson)


def get_student_attendance(
    *,
    student: Any,
    course: Any | None = None,
    group: Any | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
) -> QuerySet[AttendanceRecord]:
    """Возвращает посещаемость студента."""

    return get_attendance_queryset(
        student=student,
        course=course,
        group=group,
        date_from=date_from,
        date_to=date_to,
    )


def get_absences_for_student(
    *,
    student: Any,
    course: Any | None = None,
    group: Any | None = None,
) -> QuerySet[AttendanceRecord]:
    """Возвращает неуважительные пропуски студента."""

    return get_attendance_queryset(
        student=student,
        course=course,
        group=group,
        status=AttendanceStatus.ABSENT,
    )


def get_excused_absences_for_student(
    *,
    student: Any,
    course: Any | None = None,
    group: Any | None = None,
) -> QuerySet[AttendanceRecord]:
    """Возвращает уважительные пропуски студента."""

    return get_attendance_queryset(
        student=student,
        course=course,
        group=group,
        status=AttendanceStatus.EXCUSED,
    )


def get_lates_for_student(
    *,
    student: Any,
    course: Any | None = None,
    group: Any | None = None,
) -> QuerySet[AttendanceRecord]:
    """Возвращает опоздания студента."""

    return get_attendance_queryset(
        student=student,
        course=course,
        group=group,
        status=AttendanceStatus.LATE,
    )
