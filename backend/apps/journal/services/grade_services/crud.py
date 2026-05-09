from __future__ import annotations

import logging
from typing import Any

from django.db import transaction

from apps.journal.models import JournalGrade, JournalLesson

from .validators import normalize_grade, validate_grade_limit

logger = logging.getLogger(__name__)


@transaction.atomic
def create_journal_grade(
    *,
    lesson: JournalLesson,
    student,
    grade_type: str,
    scale: str,
    graded_by=None,
    score_five: int | None = None,
    is_passed: bool | None = None,
    weight: int = 1,
    comment: str = "",
    is_auto: bool = False,
    submission=None,
    grade_record=None,
) -> JournalGrade:
    """Создаёт оценку в журнале.

    Поддерживаются только:
    - пятибалльная оценка от 1 до 5;
    - зачёт/незачёт.
    """

    logger.info(
        "create_journal_grade started lesson_id=%s student_id=%s scale=%s",
        lesson.id,
        getattr(student, "id", None),
        scale,
    )

    validate_grade_limit(
        lesson=lesson,
        student=student,
    )

    grade = JournalGrade(
        lesson=lesson,
        student=student,
        graded_by=graded_by,
        grade_type=grade_type,
        scale=scale,
        score_five=score_five,
        is_passed=is_passed,
        weight=weight,
        comment=comment,
        is_auto=is_auto,
        submission=submission,
        grade_record=grade_record,
    )

    normalize_grade(grade)

    grade.full_clean()
    grade.save()

    logger.info("create_journal_grade completed grade_id=%s", grade.id)
    return grade


@transaction.atomic
def update_journal_grade(
    grade: JournalGrade,
    **fields: Any,
) -> JournalGrade:
    """Обновляет оценку журнала."""

    logger.info("update_journal_grade started grade_id=%s", grade.id)

    for field_name, value in fields.items():
        setattr(grade, field_name, value)

    validate_grade_limit(
        lesson=grade.lesson,
        student=grade.student,
        current_grade=grade,
    )

    normalize_grade(grade)

    grade.full_clean()
    grade.save()

    logger.info("update_journal_grade completed grade_id=%s", grade.id)
    return grade


@transaction.atomic
def delete_journal_grade(grade: JournalGrade) -> None:
    """Удаляет оценку журнала."""

    logger.info("delete_journal_grade started grade_id=%s", grade.id)
    grade.delete()
    logger.info("delete_journal_grade completed")
