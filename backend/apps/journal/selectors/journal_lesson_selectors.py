from __future__ import annotations

from datetime import date
from typing import Any

from django.db.models import Q, QuerySet
from django.shortcuts import get_object_or_404

from apps.journal.models import AttendanceRecord, JournalGrade, JournalLesson


def get_journal_lessons_queryset(
    *,
    course: Any | None = None,
    group: Any | None = None,
    teacher: Any | None = None,
    student: Any | None = None,
    status: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
) -> QuerySet[JournalLesson]:
    """Возвращает базовый queryset занятий журнала с фильтрами."""

    queryset = (
        JournalLesson.objects.select_related(
            "course",
            "group",
            "teacher",
            "course_lesson",
        )
        .all()
        .order_by("-date", "lesson_number", "-id")
    )

    if course is not None:
        queryset = queryset.filter(course=course)

    if group is not None:
        queryset = queryset.filter(group=group)

    if teacher is not None:
        queryset = queryset.filter(teacher=teacher)

    if status:
        queryset = queryset.filter(status=status)

    if date_from is not None:
        queryset = queryset.filter(date__gte=date_from)

    if date_to is not None:
        queryset = queryset.filter(date__lte=date_to)

    if student is not None:
        attendance_lesson_ids = AttendanceRecord.objects.filter(
            student=student,
        ).values("lesson_id")

        grade_lesson_ids = JournalGrade.objects.filter(
            student=student,
        ).values("lesson_id")

        queryset = queryset.filter(
            Q(id__in=attendance_lesson_ids) | Q(id__in=grade_lesson_ids)
        ).distinct()

    return queryset


def get_journal_lesson_by_id(lesson_id: int) -> JournalLesson:
    """Возвращает занятие журнала по id или 404."""

    return get_object_or_404(
        get_journal_lessons_queryset(),
        id=lesson_id,
    )


def get_journal_lesson_by_course_group_date(
    *,
    course: Any,
    group: Any,
    lesson_date: date,
    lesson_number: int | None = None,
) -> JournalLesson | None:
    """Ищет занятие по курсу, группе, дате и номеру пары."""

    queryset = get_journal_lessons_queryset(
        course=course,
        group=group,
        date_from=lesson_date,
        date_to=lesson_date,
    )

    if lesson_number is not None:
        queryset = queryset.filter(lesson_number=lesson_number)

    return queryset.first()


def get_lessons_for_course_group(
    *,
    course: Any,
    group: Any,
) -> QuerySet[JournalLesson]:
    """Возвращает занятия конкретного курса и группы."""

    return get_journal_lessons_queryset(
        course=course,
        group=group,
    )


def get_lessons_for_teacher(
    *,
    teacher: Any,
    date_from: date | None = None,
    date_to: date | None = None,
) -> QuerySet[JournalLesson]:
    """Возвращает занятия преподавателя."""

    return get_journal_lessons_queryset(
        teacher=teacher,
        date_from=date_from,
        date_to=date_to,
    )


def get_lessons_for_student(
    *,
    student: Any,
    course: Any | None = None,
    group: Any | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
) -> QuerySet[JournalLesson]:
    """Возвращает занятия, связанные со студентом через посещаемость или оценки."""

    return get_journal_lessons_queryset(
        student=student,
        course=course,
        group=group,
        date_from=date_from,
        date_to=date_to,
    )


def search_journal_lessons(query: str) -> QuerySet[JournalLesson]:
    """Поиск занятий по теме, курсу, группе, преподавателю."""

    query = query.strip()

    if not query:
        return get_journal_lessons_queryset().none()

    return get_journal_lessons_queryset().filter(
        Q(planned_topic__icontains=query)
        | Q(actual_topic__icontains=query)
        | Q(homework__icontains=query)
        | Q(teacher_comment__icontains=query)
        | Q(course__title__icontains=query)
        | Q(course__code__icontains=query)
        | Q(group__name__icontains=query)
        | Q(group__code__icontains=query)
        | Q(teacher__email__icontains=query)
    )
