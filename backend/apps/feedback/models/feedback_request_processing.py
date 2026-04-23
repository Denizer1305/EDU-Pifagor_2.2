from __future__ import annotations

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.feedback.models.base import TimeStampedModel, normalize_text
from apps.feedback.models.feedback_request import FeedbackRequest


class FeedbackRequestProcessing(TimeStampedModel):
    class Meta:
        db_table = "feedback_request_processing"
        verbose_name = "Обработка обращения"
        verbose_name_plural = "Обработка обращений"
        indexes = [
            models.Index(fields=("assigned_to",)),
            models.Index(fields=("processed_by",)),
            models.Index(fields=("processed_at",)),
            models.Index(fields=("is_spam_suspected",)),
        ]

    feedback_request = models.OneToOneField(
        FeedbackRequest,
        on_delete=models.CASCADE,
        related_name="processing",
        verbose_name="Обращение",
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="assigned_feedback_requests",
        null=True,
        blank=True,
        verbose_name="Назначено на",
    )
    assigned_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Дата назначения",
    )
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="processed_feedback_requests",
        null=True,
        blank=True,
        verbose_name="Обработано пользователем",
    )
    processed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Дата обработки",
    )
    reply_message = models.TextField(
        blank=True,
        verbose_name="Ответ пользователю",
    )
    internal_note = models.TextField(
        blank=True,
        verbose_name="Внутренняя заметка",
    )
    is_spam_suspected = models.BooleanField(
        default=False,
        verbose_name="Подозрение на спам",
    )

    def clean(self):
        errors: dict[str, str] = {}

        if self.processed_at and not self.processed_by:
            errors["processed_by"] = (
                "Для обработанного обращения нужно указать пользователя обработки."
            )

        if self.processed_by and not self.processed_at:
            errors["processed_at"] = (
                "Для обработанного обращения нужно указать дату обработки."
            )

        final_statuses = {
            FeedbackRequest.StatusChoices.RESOLVED,
            FeedbackRequest.StatusChoices.REJECTED,
            FeedbackRequest.StatusChoices.SPAM,
            FeedbackRequest.StatusChoices.ARCHIVED,
        }

        if (
            self.feedback_request.status in final_statuses
            and self.processed_at is None
        ):
            errors["processed_at"] = (
                "Финальный статус требует заполненной даты обработки."
            )

        if (
            self.feedback_request.status == FeedbackRequest.StatusChoices.SPAM
            and not self.is_spam_suspected
        ):
            errors["is_spam_suspected"] = (
                "Для статуса 'Спам' нужно установить признак подозрения на спам."
            )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.reply_message = normalize_text(self.reply_message)
        self.internal_note = normalize_text(self.internal_note)

        if self.assigned_to and self.assigned_at is None:
            self.assigned_at = timezone.now()

        if (
            self.feedback_request.status == FeedbackRequest.StatusChoices.SPAM
            and not self.is_spam_suspected
        ):
            self.is_spam_suspected = True

        super().save(*args, **kwargs)

    @property
    def is_processed(self) -> bool:
        return self.processed_at is not None

    def __str__(self) -> str:
        return f"Обработка обращения #{self.feedback_request_id}"
