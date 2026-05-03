from __future__ import annotations

from apps.journal.models import JournalGrade, JournalLesson
from apps.journal.models.choices import GradeScale, GradeType

from .crud import create_journal_grade


def create_five_point_grade(
    *,
    lesson: JournalLesson,
    student,
    score: int,
    grade_type: str = GradeType.CLASSWORK,
    graded_by=None,
    weight: int = 1,
    comment: str = "",
    is_auto: bool = False,
    submission=None,
    grade_record=None,
) -> JournalGrade:
    """Создаёт обычную оценку от 1 до 5."""

    return create_journal_grade(
        lesson=lesson,
        student=student,
        graded_by=graded_by,
        grade_type=grade_type,
        scale=GradeScale.FIVE_POINT,
        score_five=score,
        weight=weight,
        comment=comment,
        is_auto=is_auto,
        submission=submission,
        grade_record=grade_record,
    )


def create_pass_fail_grade(
    *,
    lesson: JournalLesson,
    student,
    is_passed: bool,
    grade_type: str = GradeType.CREDIT,
    graded_by=None,
    weight: int = 1,
    comment: str = "",
    is_auto: bool = False,
    submission=None,
    grade_record=None,
) -> JournalGrade:
    """Создаёт зачёт/незачёт."""

    return create_journal_grade(
        lesson=lesson,
        student=student,
        graded_by=graded_by,
        grade_type=grade_type,
        scale=GradeScale.PASS_FAIL,
        is_passed=is_passed,
        weight=weight,
        comment=comment,
        is_auto=is_auto,
        submission=submission,
        grade_record=grade_record,
    )
