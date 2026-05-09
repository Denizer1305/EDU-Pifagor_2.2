from __future__ import annotations

from typing import Any

from django.db.models import QuerySet
from django.shortcuts import get_object_or_404

from apps.journal.models import JournalSummary


def get_journal_summary_queryset(
    *,
    course: Any | None = None,
    group: Any | None = None,
    student: Any | None = None,
    only_group_summary: bool = False,
    only_student_summary: bool = False,
) -> QuerySet[JournalSummary]:
    """Возвращает queryset сводок журнала."""

    queryset = (
        JournalSummary.objects.select_related(
            "course",
            "group",
            "student",
        )
        .all()
        .order_by("-calculated_at", "-id")
    )

    if course is not None:
        queryset = queryset.filter(course=course)

    if group is not None:
        queryset = queryset.filter(group=group)

    if student is not None:
        queryset = queryset.filter(student=student)

    if only_group_summary:
        queryset = queryset.filter(student__isnull=True)

    if only_student_summary:
        queryset = queryset.filter(student__isnull=False)

    return queryset


def get_journal_summary_by_id(summary_id: int) -> JournalSummary:
    """Возвращает сводку журнала по id или 404."""

    return get_object_or_404(
        get_journal_summary_queryset(),
        id=summary_id,
    )


def get_group_journal_summary(
    *,
    course: Any,
    group: Any,
) -> JournalSummary | None:
    """Возвращает групповую сводку журнала."""

    return get_journal_summary_queryset(
        course=course,
        group=group,
        only_group_summary=True,
    ).first()


def get_student_journal_summary(
    *,
    course: Any,
    group: Any,
    student: Any,
) -> JournalSummary | None:
    """Возвращает индивидуальную сводку студента."""

    return get_journal_summary_queryset(
        course=course,
        group=group,
        student=student,
    ).first()


def get_student_summaries(student: Any) -> QuerySet[JournalSummary]:
    """Возвращает все сводки конкретного студента."""

    return get_journal_summary_queryset(
        student=student,
        only_student_summary=True,
    )


def get_group_student_summaries(
    *,
    course: Any,
    group: Any,
) -> QuerySet[JournalSummary]:
    """Возвращает индивидуальные сводки студентов группы по курсу."""

    return get_journal_summary_queryset(
        course=course,
        group=group,
        only_student_summary=True,
    )
