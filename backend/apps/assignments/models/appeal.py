from __future__ import annotations

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from apps.assignments.models.base import TimeStampedModel


class Appeal(TimeStampedModel):
    class StatusChoices(models.TextChoices):
        PENDING = "pending", "Ожидает"
        IN_PROGRESS = "in_progress", "В работе"
        APPROVED = "approved", "Удовлетворена"
        REJECTED = "rejected", "Отклонена"
        CLOSED = "closed", "Закрыта"

    submission = models.ForeignKey(
        "assignments.Submission",
        on_delete=models.CASCADE,
        related_name="appeals",
        verbose_name="Сдача",
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="appeals",
        verbose_name="Студент",
    )
    reason = models.TextField(
        verbose_name="Причина обращения",
    )
    status = models.CharField(
        max_length=32,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING,
        verbose_name="Статус",
    )
    resolution = models.TextField(
        blank=True,
        verbose_name="Решение",
    )
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="resolved_appeals",
        null=True,
        blank=True,
        verbose_name="Рассмотрел",
    )
    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Дата решения",
    )

    class Meta:
        db_table = "assignments_appeal"
        verbose_name = "Апелляция"
        verbose_name_plural = "Апелляции"
        indexes = [
            models.Index(fields=("submission", "status")),
            models.Index(fields=("student",)),
        ]

    def clean(self):
        if self.submission.student_id != self.student_id:
            raise ValidationError(
                {"student": "Апелляцию может подать только автор сдачи."}
            )

    def __str__(self) -> str:
        return f"Апелляция: {self.submission}"
