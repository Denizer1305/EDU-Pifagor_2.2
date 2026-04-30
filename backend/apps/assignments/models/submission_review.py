from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.assignments.models.base import TimeStampedModel


class SubmissionReview(TimeStampedModel):
    class ReviewStatusChoices(models.TextChoices):
        PENDING = "pending", "Ожидает"
        IN_REVIEW = "in_review", "На проверке"
        REVIEWED = "reviewed", "Проверено"
        RETURNED = "returned", "Возвращено"
        APPROVED = "approved", "Принято"
        REJECTED = "rejected", "Отклонено"

    submission = models.OneToOneField(
        "assignments.Submission",
        on_delete=models.CASCADE,
        related_name="review",
        verbose_name="Сдача",
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="submission_reviews",
        null=True,
        blank=True,
        verbose_name="Проверяющий",
    )
    review_status = models.CharField(
        max_length=32,
        choices=ReviewStatusChoices.choices,
        default=ReviewStatusChoices.PENDING,
        verbose_name="Статус проверки",
    )
    feedback = models.TextField(
        blank=True,
        verbose_name="Обратная связь",
    )
    private_note = models.TextField(
        blank=True,
        verbose_name="Внутренняя заметка",
    )
    score = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Балл по проверке",
    )
    passed = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Пройдено",
    )
    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Проверено",
    )

    class Meta:
        db_table = "assignments_submission_review"
        verbose_name = "Проверка сдачи"
        verbose_name_plural = "Проверки сдач"

    def __str__(self) -> str:
        return f"Проверка: {self.submission}"
