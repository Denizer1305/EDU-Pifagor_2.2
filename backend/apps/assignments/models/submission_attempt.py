from __future__ import annotations

from django.db import models

from apps.assignments.models.base import TimeStampedModel


class SubmissionAttempt(TimeStampedModel):
    class StatusChoices(models.TextChoices):
        DRAFT = "draft", "Черновик"
        IN_PROGRESS = "in_progress", "В процессе"
        SUBMITTED = "submitted", "Отправлено"
        CANCELLED = "cancelled", "Отменено"
        EXPIRED = "expired", "Истекло"

    submission = models.ForeignKey(
        "assignments.Submission",
        on_delete=models.CASCADE,
        related_name="attempts",
        verbose_name="Сдача",
    )
    attempt_number = models.PositiveIntegerField(
        verbose_name="Номер попытки",
    )
    started_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Начато",
    )
    submitted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Отправлено",
    )
    time_spent_minutes = models.PositiveIntegerField(
        default=0,
        verbose_name="Потрачено времени, мин",
    )
    status = models.CharField(
        max_length=32,
        choices=StatusChoices.choices,
        default=StatusChoices.DRAFT,
        verbose_name="Статус",
    )
    snapshot_json = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Снимок данных JSON",
    )

    class Meta:
        db_table = "assignments_submission_attempt"
        verbose_name = "Попытка сдачи"
        verbose_name_plural = "Попытки сдачи"
        constraints = [
            models.UniqueConstraint(
                fields=("submission", "attempt_number"),
                name="uniq_submission_attempt_number",
            ),
        ]
        ordering = ("attempt_number", "id")

    def __str__(self) -> str:
        return f"Попытка #{self.attempt_number}"
