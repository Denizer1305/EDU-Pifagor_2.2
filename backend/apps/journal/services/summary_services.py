from __future__ import annotations

import logging
from decimal import Decimal

from django.db import transaction
from django.db.models import Avg
from django.utils import timezone

from apps.journal.models import (
    AttendanceRecord,
    JournalGrade,
    JournalLesson,
    JournalSummary,
    TopicProgress,
)
from apps.journal.models.choices import (
    AttendanceStatus,
    GradeScale,
    JournalLessonStatus,
    TopicProgressStatus,
)

logger = logging.getLogger(__name__)


def _percent(*, part: int, total: int) -> Decimal:
    if total <= 0:
        return Decimal("0.00")

    return ((Decimal(part) / Decimal(total)) * Decimal("100")).quantize(Decimal("0.01"))


def _get_conducted_lessons_queryset(*, course_id: int, group_id: int):
    return JournalLesson.objects.filter(
        course_id=course_id,
        group_id=group_id,
        status=JournalLessonStatus.CONDUCTED,
    )


def _calculate_attendance_stats(
    *,
    course_id: int,
    group_id: int,
    student_id: int | None,
) -> dict[str, int | Decimal]:
    lessons = _get_conducted_lessons_queryset(
        course_id=course_id,
        group_id=group_id,
    )

    total_lessons = lessons.count()

    attendance = AttendanceRecord.objects.filter(
        lesson__course_id=course_id,
        lesson__group_id=group_id,
        lesson__status=JournalLessonStatus.CONDUCTED,
    )

    if student_id is not None:
        attendance = attendance.filter(student_id=student_id)

    attended_lessons = attendance.filter(
        status__in=[
            AttendanceStatus.PRESENT,
            AttendanceStatus.LATE,
        ],
    ).count()

    absent_lessons = attendance.filter(
        status=AttendanceStatus.ABSENT,
    ).count()

    return {
        "total_lessons": total_lessons,
        "attended_lessons": attended_lessons,
        "absent_lessons": absent_lessons,
        "attendance_percent": _percent(
            part=attended_lessons,
            total=total_lessons,
        ),
    }


def _calculate_grade_stats(
    *,
    course_id: int,
    group_id: int,
    student_id: int | None,
) -> dict[str, Decimal | int]:
    grades = JournalGrade.objects.filter(
        lesson__course_id=course_id,
        lesson__group_id=group_id,
        lesson__status=JournalLessonStatus.CONDUCTED,
    )

    if student_id is not None:
        grades = grades.filter(student_id=student_id)

    five_point_grades = grades.filter(
        scale=GradeScale.FIVE_POINT,
        score_five__isnull=False,
    )

    avg_score = five_point_grades.aggregate(value=Avg("score_five"))["value"]

    failed_credit_count = grades.filter(
        scale=GradeScale.PASS_FAIL,
        is_passed=False,
    ).count()

    bad_mark_count = five_point_grades.filter(score_five__lte=2).count()

    return {
        "avg_score": (
            Decimal(str(avg_score)).quantize(Decimal("0.01"))
            if avg_score is not None
            else None
        ),
        "debt_count": failed_credit_count + bad_mark_count,
    }


def _calculate_topic_progress_stats(
    *,
    course_id: int,
    group_id: int,
) -> dict[str, int | Decimal]:
    progress = TopicProgress.objects.filter(
        course_id=course_id,
        group_id=group_id,
    )

    total_topics = progress.count()
    completed_topics = progress.filter(
        status=TopicProgressStatus.COMPLETED,
    ).count()
    topics_behind = progress.filter(
        status=TopicProgressStatus.BEHIND,
    ).count()

    return {
        "total_topics": total_topics,
        "completed_topics": completed_topics,
        "topics_behind": topics_behind,
        "progress_percent": _percent(
            part=completed_topics,
            total=total_topics,
        ),
    }


@transaction.atomic
def recalculate_journal_summary(
    *,
    course_id: int,
    group_id: int,
    student_id: int | None = None,
) -> JournalSummary:
    """Пересчитывает сводку журнала.

    Если student_id передан — пересчитывается сводка конкретного студента.
    Если student_id не передан — пересчитывается групповая сводка.
    """

    logger.info(
        "recalculate_journal_summary started course_id=%s group_id=%s student_id=%s",
        course_id,
        group_id,
        student_id,
    )

    attendance_stats = _calculate_attendance_stats(
        course_id=course_id,
        group_id=group_id,
        student_id=student_id,
    )
    grade_stats = _calculate_grade_stats(
        course_id=course_id,
        group_id=group_id,
        student_id=student_id,
    )
    topic_stats = _calculate_topic_progress_stats(
        course_id=course_id,
        group_id=group_id,
    )

    summary, _ = JournalSummary.objects.update_or_create(
        course_id=course_id,
        group_id=group_id,
        student_id=student_id,
        defaults={
            "total_lessons": attendance_stats["total_lessons"],
            "attended_lessons": attendance_stats["attended_lessons"],
            "absent_lessons": attendance_stats["absent_lessons"],
            "attendance_percent": attendance_stats["attendance_percent"],
            "avg_score": grade_stats["avg_score"],
            "debt_count": grade_stats["debt_count"],
            "total_topics": topic_stats["total_topics"],
            "completed_topics": topic_stats["completed_topics"],
            "topics_behind": topic_stats["topics_behind"],
            "progress_percent": topic_stats["progress_percent"],
            "calculated_at": timezone.now(),
        },
    )

    logger.info(
        "recalculate_journal_summary completed summary_id=%s course_id=%s "
        "group_id=%s student_id=%s",
        summary.id,
        course_id,
        group_id,
        student_id,
    )

    return summary
