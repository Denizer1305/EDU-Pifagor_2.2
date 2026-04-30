from __future__ import annotations

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.course.models.base import TimeStampedModel


class CourseEnrollment(TimeStampedModel):
    class StatusChoices(models.TextChoices):
        ENROLLED = "enrolled", "Зачислен"
        IN_PROGRESS = "in_progress", "Проходит"
        COMPLETED = "completed", "Завершён"
        CANCELLED = "cancelled", "Отменён"
        ARCHIVED = "archived", "Архив"

    class Meta:
        db_table = "course_enrollment"
        verbose_name = "Запись на курс"
        verbose_name_plural = "Записи на курс"
        ordering = ("-created_at",)
        constraints = [
            models.UniqueConstraint(
                fields=("course", "student"),
                name="unique_course_student_enrollment",
            ),
        ]
        indexes = [
            models.Index(fields=("course", "status")),
            models.Index(fields=("student", "status")),
        ]

    course = models.ForeignKey(
        "course.Course",
        on_delete=models.CASCADE,
        related_name="enrollments",
        verbose_name="Курс",
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="course_enrollments",
        verbose_name="Студент",
    )
    assignment = models.ForeignKey(
        "course.CourseAssignment",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="enrollments",
        verbose_name="Назначение",
    )

    status = models.CharField(
        max_length=24,
        choices=StatusChoices.choices,
        default=StatusChoices.ENROLLED,
        verbose_name="Статус",
    )
    enrolled_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="Дата зачисления",
    )
    started_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Дата начала",
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Дата завершения",
    )
    last_activity_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Последняя активность",
    )
    progress_percent = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="Прогресс (%)",
    )

    def clean(self):
        errors = {}

        if self.assignment_id and self.assignment.course_id != self.course_id:
            errors["assignment"] = "Назначение должно относиться к этому же курсу."

        if self.progress_percent < 0 or self.progress_percent > 100:
            errors["progress_percent"] = "Прогресс должен быть в диапазоне от 0 до 100."

        if self.status == self.StatusChoices.COMPLETED and self.completed_at is None:
            errors["completed_at"] = "Для завершённого курса нужна дата завершения."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if self.status == self.StatusChoices.IN_PROGRESS and self.started_at is None:
            self.started_at = timezone.now()

        if self.status == self.StatusChoices.COMPLETED:
            if self.started_at is None:
                self.started_at = timezone.now()
            if self.completed_at is None:
                self.completed_at = timezone.now()
            self.progress_percent = 100

        if self.progress_percent > 100:
            self.progress_percent = 100

        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.student} — {self.course}"
