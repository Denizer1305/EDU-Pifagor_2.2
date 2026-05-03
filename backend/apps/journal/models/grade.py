from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.journal.models.choices import GradeScale, GradeType


class JournalGrade(models.Model):
    """Оценка студента в журнале.

    Поддерживает российскую систему:
    - пятибалльная шкала: 1, 2, 3, 4, 5;
    - зачёт / незачёт.

    За одно занятие студент может получить несколько оценок.
    """

    lesson = models.ForeignKey(
        "journal.JournalLesson",
        on_delete=models.CASCADE,
        related_name="grades",
        verbose_name=_("Занятие"),
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="journal_grades",
        verbose_name=_("Студент"),
    )

    grade_type = models.CharField(
        max_length=30,
        choices=GradeType.choices,
        default=GradeType.CURRENT,
        db_index=True,
        verbose_name=_("Тип оценки"),
    )
    scale = models.CharField(
        max_length=20,
        choices=GradeScale.choices,
        default=GradeScale.FIVE_POINT,
        verbose_name=_("Шкала оценивания"),
    )

    score_five = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
        ],
        verbose_name=_("Оценка от 1 до 5"),
    )
    is_passed = models.BooleanField(
        null=True,
        blank=True,
        verbose_name=_("Зачёт получен"),
    )

    weight = models.PositiveSmallIntegerField(
        default=1,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(10),
        ],
        verbose_name=_("Вес оценки"),
    )
    comment = models.TextField(
        blank=True,
        verbose_name=_("Комментарий"),
    )

    is_auto = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name=_("Выставлена автоматически"),
    )
    graded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="journal_grades_given",
        verbose_name=_("Кем выставлена"),
    )

    submission = models.ForeignKey(
        "assignments.Submission",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="journal_grades",
        verbose_name=_("Сдача задания"),
    )
    grade_record = models.ForeignKey(
        "assignments.GradeRecord",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="journal_grades",
        verbose_name=_("Запись оценки из модуля заданий"),
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Дата создания"),
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Дата обновления"),
    )

    class Meta:
        db_table = "journal_grade"
        verbose_name = _("Оценка журнала")
        verbose_name_plural = _("Оценки журнала")
        ordering = ["-lesson__date", "student", "grade_type", "id"]
        indexes = [
            models.Index(
                fields=["lesson", "student"],
                name="idx_jgrade_lesson_student",
            ),
            models.Index(
                fields=["student", "grade_type"],
                name="idx_jgrade_student_type",
            ),
            models.Index(
                fields=["grade_type"],
                name="idx_jgrade_type",
            ),
            models.Index(
                fields=["scale"],
                name="idx_jgrade_scale",
            ),
            models.Index(
                fields=["is_auto"],
                name="idx_jgrade_is_auto",
            ),
        ]
        constraints = [
            models.CheckConstraint(
                name="chk_jgrade_score_five_range",
                check=(
                    models.Q(score_five__isnull=True)
                    | models.Q(score_five__gte=1, score_five__lte=5)
                ),
            ),
            models.CheckConstraint(
                name="chk_jgrade_scale_value_consistency",
                check=(
                    models.Q(
                        scale=GradeScale.FIVE_POINT,
                        score_five__isnull=False,
                        is_passed__isnull=True,
                    )
                    | models.Q(
                        scale=GradeScale.PASS_FAIL,
                        score_five__isnull=True,
                        is_passed__isnull=False,
                    )
                ),
            ),
            models.UniqueConstraint(
                fields=["submission"],
                condition=models.Q(submission__isnull=False),
                name="uniq_journal_grade_submission",
            ),
            models.UniqueConstraint(
                fields=["grade_record"],
                condition=models.Q(grade_record__isnull=False),
                name="uniq_journal_grade_record",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.student} — {self.lesson} — {self.display_value}"

    @property
    def display_value(self) -> str:
        if self.scale == GradeScale.FIVE_POINT:
            return str(self.score_five)

        if self.is_passed is True:
            return _("Зачёт")

        if self.is_passed is False:
            return _("Незачёт")

        return "-"

    @property
    def numeric_value_for_average(self) -> Decimal | None:
        if self.scale != GradeScale.FIVE_POINT:
            return None

        if self.score_five is None:
            return None

        return Decimal(str(self.score_five))

    def clean(self) -> None:
        errors: dict[str, str] = {}

        if self.scale == GradeScale.FIVE_POINT:
            if self.score_five is None:
                errors["score_five"] = _(
                    "Для пятибалльной шкалы нужно указать оценку от 1 до 5."
                )

            if self.is_passed is not None:
                errors["is_passed"] = _(
                    "Для пятибалльной шкалы поле зачёт/незачёт не заполняется."
                )

        elif self.scale == GradeScale.PASS_FAIL:
            if self.is_passed is None:
                errors["is_passed"] = _(
                    "Для шкалы зачёт/незачёт нужно указать результат."
                )

            if self.score_five is not None:
                errors["score_five"] = _(
                    "Для шкалы зачёт/незачёт пятибалльная оценка не заполняется."
                )

        if self.submission_id and self.student_id:
            if self.submission.student_id != self.student_id:
                errors["submission"] = _("Сдача задания принадлежит другому студенту.")

        if self.grade_record_id and self.student_id:
            if self.grade_record.student_id != self.student_id:
                errors["grade_record"] = _(
                    "Запись оценки принадлежит другому студенту."
                )

        if self.submission_id and self.grade_record_id:
            grade_record_submission_id = getattr(
                self.grade_record,
                "submission_id",
                None,
            )

            if (
                grade_record_submission_id is not None
                and grade_record_submission_id != self.submission_id
            ):
                errors["grade_record"] = _(
                    "Запись оценки не относится к выбранной сдаче задания."
                )

        if errors:
            raise ValidationError(errors)
