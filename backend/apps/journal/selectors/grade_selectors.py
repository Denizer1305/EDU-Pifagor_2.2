from __future__ import annotations

from datetime import date
from typing import Any

from django.db.models import Q, QuerySet
from django.shortcuts import get_object_or_404

from apps.journal.models import JournalGrade
from apps.journal.models.choices import GradeScale, GradeType


def get_journal_grades_queryset(
    *,
    lesson: Any | None = None,
    student: Any | None = None,
    course: Any | None = None,
    group: Any | None = None,
    teacher: Any | None = None,
    grade_type: str | None = None,
    scale: str | None = None,
    is_auto: bool | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
) -> QuerySet[JournalGrade]:
    """Возвращает queryset оценок журнала с фильтрами."""

    queryset = (
        JournalGrade.objects.select_related(
            "lesson",
            "lesson__course",
            "lesson__group",
            "student",
            "graded_by",
            "submission",
            "grade_record",
        )
        .all()
        .order_by("-lesson__date", "lesson__lesson_number", "student_id", "-id")
    )

    if lesson is not None:
        queryset = queryset.filter(lesson=lesson)

    if student is not None:
        queryset = queryset.filter(student=student)

    if course is not None:
        queryset = queryset.filter(lesson__course=course)

    if group is not None:
        queryset = queryset.filter(lesson__group=group)

    if teacher is not None:
        queryset = queryset.filter(lesson__teacher=teacher)

    if grade_type:
        queryset = queryset.filter(grade_type=grade_type)

    if scale:
        queryset = queryset.filter(scale=scale)

    if is_auto is not None:
        queryset = queryset.filter(is_auto=is_auto)

    if date_from is not None:
        queryset = queryset.filter(lesson__date__gte=date_from)

    if date_to is not None:
        queryset = queryset.filter(lesson__date__lte=date_to)

    return queryset


def get_journal_grade_by_id(grade_id: int) -> JournalGrade:
    """Возвращает оценку по id или 404."""

    return get_object_or_404(
        get_journal_grades_queryset(),
        id=grade_id,
    )


def get_lesson_grades(lesson: Any) -> QuerySet[JournalGrade]:
    """Возвращает все оценки конкретного занятия."""

    return get_journal_grades_queryset(lesson=lesson)


def get_student_grades(
    *,
    student: Any,
    course: Any | None = None,
    group: Any | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
) -> QuerySet[JournalGrade]:
    """Возвращает все оценки студента."""

    return get_journal_grades_queryset(
        student=student,
        course=course,
        group=group,
        date_from=date_from,
        date_to=date_to,
    )


def get_student_lesson_grades(
    *,
    lesson: Any,
    student: Any,
) -> QuerySet[JournalGrade]:
    """Возвращает оценки студента за конкретное занятие."""

    return get_journal_grades_queryset(
        lesson=lesson,
        student=student,
    )


def get_five_point_grades(
    *,
    course: Any | None = None,
    group: Any | None = None,
    student: Any | None = None,
    lesson: Any | None = None,
) -> QuerySet[JournalGrade]:
    """Возвращает оценки по пятибалльной шкале."""

    return get_journal_grades_queryset(
        course=course,
        group=group,
        student=student,
        lesson=lesson,
        scale=GradeScale.FIVE_POINT,
    )


def get_pass_fail_grades(
    *,
    course: Any | None = None,
    group: Any | None = None,
    student: Any | None = None,
    lesson: Any | None = None,
) -> QuerySet[JournalGrade]:
    """Возвращает оценки формата зачёт/незачёт."""

    return get_journal_grades_queryset(
        course=course,
        group=group,
        student=student,
        lesson=lesson,
        scale=GradeScale.PASS_FAIL,
    )


def get_credit_grades(
    *,
    course: Any | None = None,
    group: Any | None = None,
    student: Any | None = None,
    lesson: Any | None = None,
) -> QuerySet[JournalGrade]:
    """Возвращает зачёты и незачёты."""

    return get_journal_grades_queryset(
        course=course,
        group=group,
        student=student,
        lesson=lesson,
        grade_type=GradeType.CREDIT,
        scale=GradeScale.PASS_FAIL,
    )


def get_auto_grades(
    *,
    course: Any | None = None,
    group: Any | None = None,
    student: Any | None = None,
) -> QuerySet[JournalGrade]:
    """Возвращает автоматические оценки."""

    return get_journal_grades_queryset(
        course=course,
        group=group,
        student=student,
        is_auto=True,
    )


def get_manual_grades(
    *,
    course: Any | None = None,
    group: Any | None = None,
    student: Any | None = None,
) -> QuerySet[JournalGrade]:
    """Возвращает ручные оценки преподавателя."""

    return get_journal_grades_queryset(
        course=course,
        group=group,
        student=student,
        is_auto=False,
    )


def get_grades_from_submission(
    *,
    submission: Any,
) -> QuerySet[JournalGrade]:
    """Возвращает оценки, связанные с попыткой из assignments."""

    return get_journal_grades_queryset().filter(submission=submission)


def get_grade_from_grade_record(
    *,
    grade_record: Any,
) -> JournalGrade | None:
    """Возвращает оценку журнала, связанную с GradeRecord."""

    return get_journal_grades_queryset().filter(grade_record=grade_record).first()


def search_journal_grades(query: str) -> QuerySet[JournalGrade]:
    """Ищет оценки по студенту, курсу, группе, теме занятия и комментарию."""

    query = query.strip()

    if not query:
        return get_journal_grades_queryset().none()

    return get_journal_grades_queryset().filter(
        Q(comment__icontains=query)
        | Q(lesson__planned_topic__icontains=query)
        | Q(lesson__actual_topic__icontains=query)
        | Q(lesson__course__title__icontains=query)
        | Q(lesson__course__code__icontains=query)
        | Q(lesson__group__name__icontains=query)
        | Q(lesson__group__code__icontains=query)
        | Q(student__email__icontains=query)
        | Q(graded_by__email__icontains=query)
    )
