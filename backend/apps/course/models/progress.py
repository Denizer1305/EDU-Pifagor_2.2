from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.course.models.base import TimeStampedModel


class CourseProgress(TimeStampedModel):
    class Meta:
        db_table = "course_progress"
        verbose_name = "Прогресс по курсу"
        verbose_name_plural = "Прогресс по курсам"
        ordering = ("-updated_at",)

    enrollment = models.OneToOneField(
        "course.CourseEnrollment",
        on_delete=models.CASCADE,
        related_name="progress",
        verbose_name="Запись на курс",
    )

    total_lessons_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Всего уроков",
    )
    completed_lessons_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Завершено уроков",
    )
    required_lessons_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Обязательных уроков",
    )
    completed_required_lessons_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Завершено обязательных уроков",
    )

    progress_percent = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="Прогресс (%)",
    )
    spent_minutes = models.PositiveIntegerField(
        default=0,
        verbose_name="Потрачено минут",
    )

    started_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Начат",
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Завершён",
    )
    last_activity_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Последняя активность",
    )
    last_lesson = models.ForeignKey(
        "course.CourseLesson",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="last_progress_entries",
        verbose_name="Последний урок",
    )

    def clean(self):
        errors = {}

        if self.completed_lessons_count > self.total_lessons_count:
            errors["completed_lessons_count"] = (
                "Завершённых уроков не может быть больше общего количества."
            )

        if self.completed_required_lessons_count > self.required_lessons_count:
            errors["completed_required_lessons_count"] = (
                "Завершённых обязательных уроков не может быть больше общего количества обязательных."
            )

        if self.progress_percent < 0 or self.progress_percent > 100:
            errors["progress_percent"] = "Прогресс должен быть в диапазоне от 0 до 100."

        if (
            self.last_lesson_id
            and self.last_lesson.course_id != self.enrollment.course_id
        ):
            errors["last_lesson"] = "Последний урок должен относиться к тому же курсу."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if self.completed_lessons_count and self.started_at is None:
            self.started_at = timezone.now()

        if self.progress_percent >= 100 and self.completed_at is None:
            self.completed_at = timezone.now()

        if self.progress_percent > 100:
            self.progress_percent = 100

        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"Прогресс: {self.enrollment}"


class LessonProgress(TimeStampedModel):
    class StatusChoices(models.TextChoices):
        NOT_STARTED = "not_started", "Не начат"
        IN_PROGRESS = "in_progress", "В процессе"
        COMPLETED = "completed", "Завершён"
        SKIPPED = "skipped", "Пропущен"

    class Meta:
        db_table = "lesson_progress"
        verbose_name = "Прогресс по уроку"
        verbose_name_plural = "Прогресс по урокам"
        ordering = ("lesson", "id")
        constraints = [
            models.UniqueConstraint(
                fields=("enrollment", "lesson"),
                name="unique_enrollment_lesson_progress",
            ),
        ]
        indexes = [
            models.Index(fields=("lesson", "status")),
            models.Index(fields=("enrollment", "status")),
        ]

    enrollment = models.ForeignKey(
        "course.CourseEnrollment",
        on_delete=models.CASCADE,
        related_name="lesson_progresses",
        verbose_name="Запись на курс",
    )
    course_progress = models.ForeignKey(
        "course.CourseProgress",
        on_delete=models.CASCADE,
        related_name="lesson_progresses",
        null=True,
        blank=True,
        verbose_name="Прогресс по курсу",
    )
    lesson = models.ForeignKey(
        "course.CourseLesson",
        on_delete=models.CASCADE,
        related_name="lesson_progresses",
        verbose_name="Урок",
    )

    status = models.CharField(
        max_length=24,
        choices=StatusChoices.choices,
        default=StatusChoices.NOT_STARTED,
        verbose_name="Статус",
    )
    started_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Начат",
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Завершён",
    )
    last_viewed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Последний просмотр",
    )
    spent_minutes = models.PositiveIntegerField(
        default=0,
        verbose_name="Потрачено минут",
    )
    attempts_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Количество попыток",
    )
    score = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Баллы / результат",
    )

    def clean(self):
        errors = {}

        if self.lesson.course_id != self.enrollment.course_id:
            errors["lesson"] = "Урок должен относиться к тому же курсу, что и запись."

        if (
            self.course_progress_id
            and self.course_progress.enrollment_id != self.enrollment_id
        ):
            errors["course_progress"] = (
                "Прогресс по курсу должен относиться к той же записи."
            )

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

        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.enrollment} — {self.lesson}"
