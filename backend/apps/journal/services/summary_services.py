from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

from django.db.models import Avg

from apps.journal.models import (
    AttendanceRecord,
    AttendanceStatus,
    GradeScale,
    JournalGrade,
    JournalLesson,
    JournalSummary,
    LessonStatus,
    TopicProgress,
    TopicProgressStatus,
)


def recalculate_summary_for_group(
    *,
    course_id: int,
    group_id: int,
) -> JournalSummary:
    """
    Пересчитывает агрегированную сводку по всей группе (student=None).

    Вызывается из Celery-задач или сигналов после изменения данных.
    """
    lessons_qs = JournalLesson.objects.filter(
        course_id=course_id,
        group_id=group_id,
        status=LessonStatus.CONDUCTED,
    )
    total_lessons = lessons_qs.count()

    # Посещаемость по группе: считаем записи присутствия
    attended = AttendanceRecord.objects.filter(
        lesson__in=lessons_qs,
        status__in=[AttendanceStatus.PRESENT, AttendanceStatus.REMOTE],
    ).count()

    absent = AttendanceRecord.objects.filter(
        lesson__in=lessons_qs,
        status=AttendanceStatus.ABSENT,
    ).count()

    total_attendance_marks = attended + absent
    attendance_percent = (
        Decimal(attended / total_attendance_marks * 100).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        if total_attendance_marks > 0
        else Decimal("0.00")
    )

    # Средний балл (только пятибалльные оценки по проведённым занятиям)
    avg_agg = JournalGrade.objects.filter(
        lesson__in=lessons_qs,
        scale=GradeScale.FIVE_POINT,
        score_five__isnull=False,
    ).aggregate(avg=Avg("score_five"))
    avg_score = (
        Decimal(str(avg_agg["avg"])).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        if avg_agg["avg"] is not None
        else None
    )

    # Прогресс по КТП
    topic_qs = TopicProgress.objects.filter(course_id=course_id, group_id=group_id)
    total_topics = topic_qs.count()
    completed_topics = topic_qs.filter(status=TopicProgressStatus.COMPLETED).count()
    topics_behind = topic_qs.filter(status=TopicProgressStatus.BEHIND).count()
    progress_percent = (
        Decimal(completed_topics / total_topics * 100).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        if total_topics > 0
        else Decimal("0.00")
    )

    summary, _ = JournalSummary.objects.update_or_create(
        course_id=course_id,
        group_id=group_id,
        student=None,
        defaults={
            "total_lessons": total_lessons,
            "attended_lessons": attended,
            "absent_lessons": absent,
            "attendance_percent": attendance_percent,
            "avg_score": avg_score,
            "debt_count": 0,  # для группы без разбивки не считаем
            "total_topics": total_topics,
            "completed_topics": completed_topics,
            "topics_behind": topics_behind,
            "progress_percent": progress_percent,
        },
    )
    return summary


def recalculate_summary_for_student(
    *,
    course_id: int,
    group_id: int,
    student_id: int,
) -> JournalSummary:
    """
    Пересчитывает индивидуальную сводку для конкретного студента.

    Вызывается из Celery-задач или сигналов.
    """
    lessons_qs = JournalLesson.objects.filter(
        course_id=course_id,
        group_id=group_id,
        status=LessonStatus.CONDUCTED,
    )
    total_lessons = lessons_qs.count()

    # Посещаемость студента
    attended = AttendanceRecord.objects.filter(
        lesson__in=lessons_qs,
        student_id=student_id,
        status__in=[AttendanceStatus.PRESENT, AttendanceStatus.REMOTE],
    ).count()

    absent = AttendanceRecord.objects.filter(
        lesson__in=lessons_qs,
        student_id=student_id,
        status=AttendanceStatus.ABSENT,
    ).count()

    attendance_percent = (
        Decimal(attended / total_lessons * 100).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        if total_lessons > 0
        else Decimal("0.00")
    )

    # Средний балл студента
    avg_agg = JournalGrade.objects.filter(
        lesson__in=lessons_qs,
        student_id=student_id,
        scale=GradeScale.FIVE_POINT,
        score_five__isnull=False,
    ).aggregate(avg=Avg("score_five"))
    avg_score = (
        Decimal(str(avg_agg["avg"])).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        if avg_agg["avg"] is not None
        else None
    )

    # Задолженности: незачтённые зачётные оценки
    debt_count = JournalGrade.objects.filter(
        lesson__in=lessons_qs,
        student_id=student_id,
        scale=GradeScale.PASS_FAIL,
        is_passed=False,
    ).count()

    # Прогресс по КТП (общий для группы — индивидуального нет)
    topic_qs = TopicProgress.objects.filter(course_id=course_id, group_id=group_id)
    total_topics = topic_qs.count()
    completed_topics = topic_qs.filter(status=TopicProgressStatus.COMPLETED).count()
    topics_behind = topic_qs.filter(status=TopicProgressStatus.BEHIND).count()
    progress_percent = (
        Decimal(completed_topics / total_topics * 100).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        if total_topics > 0
        else Decimal("0.00")
    )

    summary, _ = JournalSummary.objects.update_or_create(
        course_id=course_id,
        group_id=group_id,
        student_id=student_id,
        defaults={
            "total_lessons": total_lessons,
            "attended_lessons": attended,
            "absent_lessons": absent,
            "attendance_percent": attendance_percent,
            "avg_score": avg_score,
            "debt_count": debt_count,
            "total_topics": total_topics,
            "completed_topics": completed_topics,
            "topics_behind": topics_behind,
            "progress_percent": progress_percent,
        },
    )
    return summary
