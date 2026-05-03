from __future__ import annotations

from django.core.exceptions import ValidationError

from apps.journal.models import JournalGrade, JournalLesson
from apps.journal.models.choices import GradeScale, GradeType

from .constants import MAX_GRADES_PER_LESSON_PER_STUDENT


def validate_grade_limit(
    *,
    lesson: JournalLesson,
    student,
    current_grade: JournalGrade | None = None,
) -> None:
    """Проверяет лимит: максимум 2 оценки за одно занятие на одного студента."""

    grades = JournalGrade.objects.filter(
        lesson=lesson,
        student=student,
    )

    if current_grade is not None and current_grade.pk:
        grades = grades.exclude(pk=current_grade.pk)

    if grades.count() >= MAX_GRADES_PER_LESSON_PER_STUDENT:
        raise ValidationError(
            {
                "student": (
                    "Нельзя поставить больше двух оценок одному студенту "
                    "за одно занятие."
                )
            }
        )


def normalize_grade(grade: JournalGrade) -> None:
    """Приводит оценку к правилам российского журнала."""

    if grade.weight <= 0:
        raise ValidationError({"weight": "Вес оценки должен быть положительным."})

    if grade.scale == GradeScale.FIVE_POINT:
        normalize_five_point_grade(grade)
        return

    if grade.scale == GradeScale.PASS_FAIL:
        normalize_pass_fail_grade(grade)
        return

    raise ValidationError(
        {"scale": "Допустимы только шкалы: оценка 1–5 или зачёт/незачёт."}
    )


def normalize_five_point_grade(grade: JournalGrade) -> None:
    """Нормализует пятибалльную оценку."""

    if grade.score_five is None:
        raise ValidationError(
            {"score_five": "Для пятибалльной оценки укажите значение от 1 до 5."}
        )

    if grade.score_five < 1 or grade.score_five > 5:
        raise ValidationError({"score_five": "Оценка должна быть от 1 до 5."})

    grade.is_passed = None


def normalize_pass_fail_grade(grade: JournalGrade) -> None:
    """Нормализует зачёт/незачёт."""

    if grade.is_passed is None:
        raise ValidationError({"is_passed": "Для зачёта/незачёта укажите результат."})

    grade.score_five = None

    if grade.grade_type != GradeType.CREDIT:
        grade.grade_type = GradeType.CREDIT
