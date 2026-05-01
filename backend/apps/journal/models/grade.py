from __future__ import annotations

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class GradeType(models.TextChoices):
    """Тип оценки в журнале."""

    CURRENT = "current", _("Текущая")
    CONTROL = "control", _("Контрольная работа")
    TEST = "test", _("Тест")
    PRACTICAL = "practical", _("Практическая работа")
    LAB = "lab", _("Лабораторная работа")
    HOMEWORK = "homework", _("Домашняя работа")
    EXAM = "exam", _("Экзамен")
    CREDIT = "credit", _("Зачёт")
    MIDTERM = "midterm", _("Промежуточная аттестация")
    FINAL = "final", _("Итоговая оценка")
    MANUAL = "manual", _("Ручная оценка")


class GradeScale(models.TextChoices):
    """Шкала оценивания."""

    FIVE_POINT = "five_point", _("Пятибалльная")
    PASS_FAIL = "pass_fail", _("Зачёт/незачёт")
    POINTS = "points", _("Баллы")
    PERCENT = "percent", _("Проценты")


class JournalGrade(models.Model):
    """
    Оценка студента в электронном журнале.

    Может быть выставлена вручную преподавателем или автоматически
    сформирована на основе данных из assignments.GradeRecord.
    Не заменяет GradeRecord — отражает его в контексте журнала.
    """

    lesson = models.ForeignKey(
        "journal.JournalLesson",
        on_delete=models.CASCADE,
        related_name="grades",
        verbose_name=_("Занятие"),
    )
    student = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="journal_grades",
        verbose_name=_("Студент"),
    )

    # --- Опциональные связи с assignments/ ---
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
        verbose_name=_("Запись оценки (assignments)"),
    )

    # --- Тип и шкала ---
    grade_type = models.CharField(
        max_length=30,
        choices=GradeType.choices,
        default=GradeType.CURRENT,
        verbose_name=_("Тип оценки"),
        db_index=True,
    )
    scale = models.CharField(
        max_length=20,
        choices=GradeScale.choices,
        default=GradeScale.FIVE_POINT,
        verbose_name=_("Шкала"),
    )

    # --- Значения оценки ---
    # Пятибалльная (1–5)
    score_five = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name=_("Оценка (5-балльная)"),
    )
    # Числовые баллы (например, за 100-балльную систему или тест)
    score_points = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name=_("Баллы"),
    )
    # Максимально возможные баллы
    max_points = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name=_("Максимум баллов"),
    )
    # Зачёт/незачёт
    is_passed = models.BooleanField(
        null=True,
        blank=True,
        verbose_name=_("Зачтено"),
    )

    # --- Вес оценки для расчёта среднего ---
    weight = models.PositiveSmallIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name=_("Вес оценки"),
    )

    # --- Мета ---
    comment = models.TextField(
        blank=True,
        verbose_name=_("Комментарий преподавателя"),
    )
    is_auto = models.BooleanField(
        default=False,
        verbose_name=_("Выставлена автоматически"),
    )

    # --- Служебные поля ---
    graded_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="given_journal_grades",
        verbose_name=_("Выставил"),
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Создано"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Обновлено"))

    class Meta:
        verbose_name = _("Оценка в журнале")
        verbose_name_plural = _("Оценки в журнале")
        db_table = "journal_grade"
        ordering = ["lesson__date", "student"]
        indexes = [
            models.Index(fields=["lesson", "student"], name="idx_jgrade_lesson_student"),
            models.Index(fields=["student", "grade_type"], name="idx_jgrade_student_type"),
            models.Index(fields=["grade_type"], name="idx_jgrade_type"),
        ]

    def __str__(self) -> str:
        value = self._display_value()
        return f"{self.student} | {self.get_grade_type_display()} | {value}"

    def _display_value(self) -> str:
        if self.scale == GradeScale.FIVE_POINT and self.score_five is not None:
            return str(self.score_five)
        if self.scale == GradeScale.PASS_FAIL and self.is_passed is not None:
            return _("Зачтено") if self.is_passed else _("Не зачтено")
        if self.score_points is not None:
            return f"{self.score_points}"
        return "—"

    @property
    def display_value(self) -> str:
        return self._display_value()
