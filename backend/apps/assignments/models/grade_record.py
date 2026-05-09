from __future__ import annotations

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from apps.assignments.models.base import TimeStampedModel


class GradeRecord(TimeStampedModel):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="grade_records",
        verbose_name="Студент",
    )
    assignment = models.ForeignKey(
        "assignments.Assignment",
        on_delete=models.CASCADE,
        related_name="grade_records",
        verbose_name="Работа",
    )
    publication = models.ForeignKey(
        "assignments.AssignmentPublication",
        on_delete=models.SET_NULL,
        related_name="grade_records",
        null=True,
        blank=True,
        verbose_name="Публикация",
    )
    submission = models.ForeignKey(
        "assignments.Submission",
        on_delete=models.SET_NULL,
        related_name="grade_records",
        null=True,
        blank=True,
        verbose_name="Сдача",
    )
    grade_value = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Значение оценки",
    )
    grade_numeric = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Числовая оценка",
    )
    grading_mode = models.CharField(
        max_length=32,
        blank=True,
        verbose_name="Режим оценивания",
    )
    is_final = models.BooleanField(
        default=True,
        verbose_name="Итоговая",
    )
    graded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="graded_records",
        null=True,
        blank=True,
        verbose_name="Оценил",
    )
    graded_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Дата оценивания",
    )

    class Meta:
        db_table = "assignments_grade_record"
        verbose_name = "Запись оценки"
        verbose_name_plural = "Записи оценок"
        indexes = [
            models.Index(fields=("student", "assignment")),
            models.Index(fields=("publication",)),
            models.Index(fields=("submission",)),
        ]

    def clean(self):
        errors: dict[str, str] = {}

        if self.submission_id and self.submission.assignment_id != self.assignment_id:
            errors["submission"] = "Сдача должна относиться к выбранной работе."

        if self.publication_id and self.publication.assignment_id != self.assignment_id:
            errors["publication"] = "Публикация должна относиться к выбранной работе."

        if self.submission_id and self.submission.student_id != self.student_id:
            errors["student"] = "Студент должен совпадать со сдачей."

        if errors:
            raise ValidationError(errors)

    def __str__(self) -> str:
        return f"{self.student} — {self.assignment}"
