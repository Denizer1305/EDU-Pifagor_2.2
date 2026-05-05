from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.feedback.models.base import normalize_text
from apps.feedback.models.feedback_request import FeedbackRequest


class FeedbackStatusHistory(models.Model):
    feedback_request = models.ForeignKey(
        FeedbackRequest,
        on_delete=models.CASCADE,
        related_name="status_history",
        verbose_name="Обращение",
    )
    from_status = models.CharField(
        max_length=32,
        blank=True,
        verbose_name="Предыдущий статус",
    )
    to_status = models.CharField(
        max_length=32,
        choices=FeedbackRequest.StatusChoices.choices,
        verbose_name="Новый статус",
    )
    comment = models.TextField(
        blank=True,
        verbose_name="Комментарий",
    )
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="feedback_status_changes",
        null=True,
        blank=True,
        verbose_name="Кто изменил",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата изменения",
        db_index=True,
    )

    class Meta:
        db_table = "feedback_status_history"
        verbose_name = "История статуса обращения"
        verbose_name_plural = "История статусов обращений"
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=("feedback_request", "created_at")),
            models.Index(fields=("to_status", "created_at")),
        ]

    def __str__(self) -> str:
        return f"{self.feedback_request_id}: {self.from_status} -> {self.to_status}"

    def save(self, *args, **kwargs):
        self.from_status = normalize_text(self.from_status)
        self.comment = normalize_text(self.comment)
        super().save(*args, **kwargs)
