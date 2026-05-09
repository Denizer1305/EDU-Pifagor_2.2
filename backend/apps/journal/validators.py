from __future__ import annotations

from datetime import date, time
from typing import Any

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from apps.journal.models import JournalGrade
from apps.journal.models.choices import GradeScale

MAX_GRADES_PER_STUDENT_LESSON = 2


def validate_lesson_time(
    *,
    started_at: time | None,
    ended_at: time | None,
) -> None:
    """Проверяет корректность времени занятия."""

    if started_at is None or ended_at is None:
        return

    if ended_at <= started_at:
        raise ValidationError(
            {
                "ended_at": _("Время окончания занятия должно быть позже начала."),
            }
        )


def validate_topic_dates(
    *,
    planned_date: date | None,
    actual_date: date | None,
) -> None:
    """Проверяет даты прохождения темы."""

    if planned_date is None or actual_date is None:
        return

    # Фактическая дата может быть раньше плановой, если тему прошли заранее.
    # Поэтому здесь оставляем только проверку типа/наличия через model fields.
    return


def validate_grade_value(
    *,
    scale: str,
    score_five: int | None = None,
    is_passed: bool | None = None,
) -> None:
    """Проверяет оценку по российской системе: 1–5 или зачёт/незачёт."""

    if scale == GradeScale.FIVE_POINT:
        if score_five is None:
            raise ValidationError(
                {
                    "score_five": _(
                        "Для пятибалльной шкалы нужно указать оценку от 1 до 5."
                    ),
                }
            )

        if score_five < 1 or score_five > 5:
            raise ValidationError(
                {
                    "score_five": _("Оценка должна быть в диапазоне от 1 до 5."),
                }
            )

        if is_passed is not None:
            raise ValidationError(
                {
                    "is_passed": _(
                        "Поле зачёта не используется для пятибалльной оценки."
                    ),
                }
            )

        return

    if scale == GradeScale.PASS_FAIL:
        if is_passed is None:
            raise ValidationError(
                {
                    "is_passed": _("Для шкалы зачёт/незачёт нужно указать результат."),
                }
            )

        if score_five is not None:
            raise ValidationError(
                {
                    "score_five": _(
                        "Пятибалльная оценка не используется для зачёта/незачёта."
                    ),
                }
            )

        return

    raise ValidationError(
        {
            "scale": _("Неподдерживаемая шкала оценки."),
        }
    )


def validate_grade_source(
    *,
    is_auto: bool,
    graded_by: Any | None = None,
    submission: Any | None = None,
    grade_record: Any | None = None,
) -> None:
    """Проверяет источник оценки: ручная или автоматическая."""

    if is_auto and submission is None and grade_record is None:
        raise ValidationError(
            {
                "submission": _(
                    "Автоматическая оценка должна быть связана с работой "
                    "или записью оценки."
                ),
            }
        )

    if not is_auto and graded_by is None:
        raise ValidationError(
            {
                "graded_by": _("Для ручной оценки нужно указать преподавателя."),
            }
        )


def validate_max_grades_per_lesson(
    *,
    lesson: Any,
    student: Any,
    exclude_grade_id: int | None = None,
    max_grades: int = MAX_GRADES_PER_STUDENT_LESSON,
) -> None:
    """Ограничивает количество оценок студента за одно занятие."""

    queryset = JournalGrade.objects.filter(
        lesson=lesson,
        student=student,
    )

    if exclude_grade_id is not None:
        queryset = queryset.exclude(id=exclude_grade_id)

    if queryset.count() >= max_grades:
        raise ValidationError(
            {
                "student": _(
                    "За одно занятие студенту можно поставить не более двух оценок."
                ),
            }
        )


def validate_unique_grade_links(
    *,
    submission: Any | None = None,
    grade_record: Any | None = None,
    exclude_grade_id: int | None = None,
) -> None:
    """Проверяет, что одна работа не попадает в журнал несколько раз."""

    queryset = JournalGrade.objects.all()

    if exclude_grade_id is not None:
        queryset = queryset.exclude(id=exclude_grade_id)

    if submission is not None and queryset.filter(submission=submission).exists():
        raise ValidationError(
            {
                "submission": _("Оценка по этой работе уже есть в журнале."),
            }
        )

    if grade_record is not None and queryset.filter(grade_record=grade_record).exists():
        raise ValidationError(
            {
                "grade_record": _("Эта запись оценки уже связана с журналом."),
            }
        )


def validate_journal_grade(
    *,
    lesson: Any,
    student: Any,
    scale: str,
    score_five: int | None = None,
    is_passed: bool | None = None,
    is_auto: bool = False,
    graded_by: Any | None = None,
    submission: Any | None = None,
    grade_record: Any | None = None,
    exclude_grade_id: int | None = None,
) -> None:
    """Комплексная проверка оценки журнала."""

    validate_grade_value(
        scale=scale,
        score_five=score_five,
        is_passed=is_passed,
    )
    validate_grade_source(
        is_auto=is_auto,
        graded_by=graded_by,
        submission=submission,
        grade_record=grade_record,
    )
    validate_max_grades_per_lesson(
        lesson=lesson,
        student=student,
        exclude_grade_id=exclude_grade_id,
    )
    validate_unique_grade_links(
        submission=submission,
        grade_record=grade_record,
        exclude_grade_id=exclude_grade_id,
    )
