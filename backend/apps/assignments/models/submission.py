from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.assignments.models.base import TimeStampedModel


class Submission(TimeStampedModel):
    class StatusChoices(models.TextChoices):
        DRAFT = "draft", "Черновик"
        IN_PROGRESS = "in_progress", "В процессе"
        SUBMITTED = "submitted", "Отправлено"
        UNDER_REVIEW = "under_review", "На проверке"
        REVIEWED = "reviewed", "Проверено"
        RETURNED_FOR_REVISION = "returned_for_revision", "Возвращено на доработку"
        ACCEPTED = "accepted", "Принято"
        REJECTED = "rejected", "Отклонено"
        CANCELLED = "cancelled", "Отменено"

    publication = models.ForeignKey(
        "assignments.AssignmentPublication",
        on_delete=models.CASCADE,
        related_name="submissions",
        verbose_name="Публикация",
    )
    assignment = models.ForeignKey(
        "assignments.Assignment",
        on_delete=models.CASCADE,
        related_name="submissions",
        verbose_name="Работа",
    )
    variant = models.ForeignKey(
        "assignments.AssignmentVariant",
        on_delete=models.SET_NULL,
        related_name="submissions",
        null=True,
        blank=True,
        verbose_name="Вариант",
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="assignment_submissions",
        verbose_name="Студент",
    )
    status = models.CharField(
        max_length=32,
        choices=StatusChoices.choices,
        default=StatusChoices.DRAFT,
        verbose_name="Статус",
    )
    attempt_number = models.PositiveIntegerField(
        default=1,
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
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Завершено",
    )
    time_spent_minutes = models.PositiveIntegerField(
        default=0,
        verbose_name="Потрачено времени, мин",
    )
    is_late = models.BooleanField(
        default=False,
        verbose_name="Просрочено",
    )
    late_minutes = models.PositiveIntegerField(
        default=0,
        verbose_name="Просрочка, мин",
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
    percentage = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Процент",
    )
    passed = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Пройдено",
    )
    checked_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Проверено",
    )
    checked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="checked_submissions",
        null=True,
        blank=True,
        verbose_name="Проверяющий",
    )

    class Meta:
        db_table = "assignments_submission"
        verbose_name = "Сдача работы"
        verbose_name_plural = "Сдачи работ"
        ordering = ("-created_at",)
        constraints = [
            models.UniqueConstraint(
                fields=("publication", "student", "attempt_number"),
                name="uniq_publication_student_attempt",
            ),
        ]
        indexes = [
            models.Index(fields=("publication", "student")),
            models.Index(fields=("assignment", "student")),
            models.Index(fields=("status",)),
        ]

    def clean(self):
        errors: dict[str, str] = {}

        if self.publication.assignment_id != self.assignment_id:
            errors["assignment"] = "Работа должна совпадать с публикацией."

        if self.variant_id and self.variant.assignment_id != self.assignment_id:
            errors["variant"] = "Вариант должен принадлежать выбранной работе."

        if self.final_score is not None and self.final_score < Decimal("0"):
            errors["final_score"] = "Итоговый балл не может быть отрицательным."

        if self.percentage is not None and (
            self.percentage < 0 or self.percentage > 100
        ):
            errors["percentage"] = "Процент должен быть в диапазоне от 0 до 100."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if (
            self.submitted_at
            and self.publication.due_at
            and self.submitted_at > self.publication.due_at
        ):
            self.is_late = True
            delta = self.submitted_at - self.publication.due_at
            self.late_minutes = max(int(delta.total_seconds() // 60), 0)

        if (
            self.status
            in {
                self.StatusChoices.SUBMITTED,
                self.StatusChoices.UNDER_REVIEW,
                self.StatusChoices.REVIEWED,
                self.StatusChoices.ACCEPTED,
                self.StatusChoices.REJECTED,
            }
            and self.submitted_at is None
        ):
            self.submitted_at = timezone.now()

        if (
            self.status
            in {
                self.StatusChoices.REVIEWED,
                self.StatusChoices.ACCEPTED,
                self.StatusChoices.REJECTED,
            }
            and self.completed_at is None
        ):
            self.completed_at = timezone.now()

        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.assignment} — {self.student}"
