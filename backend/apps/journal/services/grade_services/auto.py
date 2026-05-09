from __future__ import annotations

from django.db import transaction

from apps.journal.models import JournalGrade, JournalLesson

from .crud import create_journal_grade, update_journal_grade


@transaction.atomic
def upsert_auto_grade_from_assignment(
    *,
    lesson: JournalLesson,
    student,
    grade_type: str,
    scale: str,
    score_five: int | None = None,
    is_passed: bool | None = None,
    comment: str = "",
    submission=None,
    grade_record=None,
    graded_by=None,
) -> JournalGrade:
    """Создаёт или обновляет автоматическую оценку из assignments.

    Используется, когда тест/работа автоматически переносит результат
    в журнал и дневник студента.
    """

    existing_grade = find_existing_auto_grade(
        submission=submission,
        grade_record=grade_record,
    )

    if existing_grade is not None:
        return update_journal_grade(
            existing_grade,
            lesson=lesson,
            student=student,
            graded_by=graded_by,
            grade_type=grade_type,
            scale=scale,
            score_five=score_five,
            is_passed=is_passed,
            comment=comment,
            is_auto=True,
            submission=submission,
            grade_record=grade_record,
        )

    return create_journal_grade(
        lesson=lesson,
        student=student,
        graded_by=graded_by,
        grade_type=grade_type,
        scale=scale,
        score_five=score_five,
        is_passed=is_passed,
        comment=comment,
        is_auto=True,
        submission=submission,
        grade_record=grade_record,
    )


def find_existing_auto_grade(
    *,
    submission=None,
    grade_record=None,
) -> JournalGrade | None:
    """Ищет уже созданную автоматическую оценку."""

    if grade_record is not None:
        existing_grade = JournalGrade.objects.filter(grade_record=grade_record).first()
        if existing_grade is not None:
            return existing_grade

    if submission is not None:
        return JournalGrade.objects.filter(submission=submission).first()

    return None
