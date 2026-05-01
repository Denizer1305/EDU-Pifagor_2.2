from __future__ import annotations

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from apps.journal.models import JournalGrade, GradeScale, JournalLesson


def create_journal_grade(
    *,
    lesson: JournalLesson,
    student_id: int,
    grade_type: str,
    scale: str = GradeScale.FIVE_POINT,
    score_five: int | None = None,
    score_points=None,
    max_points=None,
    is_passed: bool | None = None,
    weight: int = 1,
    comment: str = "",
    graded_by_id: int | None = None,
    submission_id: int | None = None,
    grade_record_id: int | None = None,
    is_auto: bool = False,
) -> JournalGrade:
    """
    Выставляет оценку студенту в журнале.

    Проверяет:
    - Для пятибалльной шкалы должно быть передано score_five.
    - Для зачёт/незачёт должно быть передано is_passed.
    - Для баллов должно быть передано score_points.
    """
    _validate_grade_values(
        scale=scale,
        score_five=score_five,
        score_points=score_points,
        is_passed=is_passed,
    )

    grade = JournalGrade(
        lesson=lesson,
        student_id=student_id,
        grade_type=grade_type,
        scale=scale,
        score_five=score_five,
        score_points=score_points,
        max_points=max_points,
        is_passed=is_passed,
        weight=weight,
        comment=comment,
        graded_by_id=graded_by_id,
        submission_id=submission_id,
        grade_record_id=grade_record_id,
        is_auto=is_auto,
    )
    grade.full_clean()
    grade.save()
    return grade


def update_journal_grade(
    *,
    grade: JournalGrade,
    score_five: int | None = None,
    score_points=None,
    is_passed: bool | None = None,
    comment: str | None = None,
    weight: int | None = None,
) -> JournalGrade:
    """
    Обновляет оценку. Только переданные поля меняются.
    """
    update_fields = ["updated_at"]

    if score_five is not None:
        grade.score_five = score_five
        update_fields.append("score_five")

    if score_points is not None:
        grade.score_points = score_points
        update_fields.append("score_points")

    if is_passed is not None:
        grade.is_passed = is_passed
        update_fields.append("is_passed")

    if comment is not None:
        grade.comment = comment
        update_fields.append("comment")

    if weight is not None:
        grade.weight = weight
        update_fields.append("weight")

    _validate_grade_values(
        scale=grade.scale,
        score_five=grade.score_five,
        score_points=grade.score_points,
        is_passed=grade.is_passed,
    )

    grade.full_clean()
    grade.save(update_fields=update_fields)
    return grade


def delete_journal_grade(*, grade: JournalGrade) -> None:
    """Удаляет оценку из журнала."""
    grade.delete()


def create_grade_from_grade_record(
    *,
    lesson: JournalLesson,
    grade_record_id: int,
) -> JournalGrade:
    """
    Создаёт запись в журнале на основе assignments.GradeRecord.

    Используется при автоматической синхронизации оценок из assignments/
    в электронный журнал.
    """
    from apps.assignments.models import GradeRecord  # локальный импорт во избежание цикличности

    try:
        gr = GradeRecord.objects.select_related("student").get(pk=grade_record_id)
    except GradeRecord.DoesNotExist:
        raise ValidationError(_("GradeRecord не найден."))

    # Определяем шкалу и значение из GradeRecord
    scale = GradeScale.POINTS
    score_points = gr.grade_numeric
    score_five = None
    is_passed = None

    if gr.grading_mode == "pass_fail":
        scale = GradeScale.PASS_FAIL
        is_passed = gr.grade_value in ("passed", "credit", "зачтено")
        score_points = None
    elif gr.grading_mode == "five_point":
        scale = GradeScale.FIVE_POINT
        score_five = int(gr.grade_numeric) if gr.grade_numeric else None
        score_points = None

    return create_journal_grade(
        lesson=lesson,
        student_id=gr.student_id,
        grade_type="current",
        scale=scale,
        score_five=score_five,
        score_points=score_points,
        is_passed=is_passed,
        grade_record_id=grade_record_id,
        is_auto=True,
    )


# ---------------------------------------------------------------------------
# Внутренние валидаторы
# ---------------------------------------------------------------------------

def _validate_grade_values(
    *,
    scale: str,
    score_five: int | None,
    score_points,
    is_passed: bool | None,
) -> None:
    """Проверяет соответствие значения оценки выбранной шкале."""
    if scale == GradeScale.FIVE_POINT and score_five is None:
        raise ValidationError(
            _("Для пятибалльной шкалы необходимо указать score_five.")
        )
    if scale == GradeScale.PASS_FAIL and is_passed is None:
        raise ValidationError(
            _("Для шкалы зачёт/незачёт необходимо указать is_passed.")
        )
    if scale == GradeScale.POINTS and score_points is None:
        raise ValidationError(
            _("Для балльной шкалы необходимо указать score_points.")
        )
