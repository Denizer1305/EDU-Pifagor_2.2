from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import models

from apps.assignments.models.base import TimeStampedModel


class SubmissionAnswer(TimeStampedModel):
    class ReviewStatusChoices(models.TextChoices):
        PENDING = "pending", "Ожидает"
        AUTO_CHECKED = "auto_checked", "Автопроверено"
        REVIEWED = "reviewed", "Проверено вручную"

    submission = models.ForeignKey(
        "assignments.Submission",
        on_delete=models.CASCADE,
        related_name="answers",
        verbose_name="Сдача",
    )
    question = models.ForeignKey(
        "assignments.AssignmentQuestion",
        on_delete=models.CASCADE,
        related_name="submission_answers",
        verbose_name="Вопрос",
    )
    answer_text = models.TextField(
        blank=True,
        verbose_name="Текст ответа",
    )
    answer_json = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Ответ JSON",
    )
    selected_options_json = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Выбранные варианты JSON",
    )
    numeric_answer = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        null=True,
        blank=True,
        verbose_name="Числовой ответ",
    )
    is_correct = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Верно",
    )
    auto_score = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Автобалл",
    )
    manual_score = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Ручной балл",
    )
    final_score = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Итоговый балл",
    )
    review_status = models.CharField(
        max_length=32,
        choices=ReviewStatusChoices.choices,
        default=ReviewStatusChoices.PENDING,
        verbose_name="Статус проверки",
    )

    class Meta:
        db_table = "assignments_submission_answer"
        verbose_name = "Ответ на вопрос"
        verbose_name_plural = "Ответы на вопросы"
        constraints = [
            models.UniqueConstraint(
                fields=("submission", "question"),
                name="uniq_submission_question_answer",
            ),
        ]
        indexes = [
            models.Index(fields=("submission",)),
            models.Index(fields=("question",)),
        ]

    def clean(self):
        errors: dict[str, str] = {}

        if self.question.assignment_id != self.submission.assignment_id:
            errors["question"] = "Вопрос должен принадлежать работе в выбранной сдаче."

        if errors:
            raise ValidationError(errors)

    def __str__(self) -> str:
        return f"Ответ #{self.pk or 'new'}"
