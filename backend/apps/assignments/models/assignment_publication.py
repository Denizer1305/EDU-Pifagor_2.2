from __future__ import annotations

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from apps.assignments.models.base import TimeStampedModel, normalize_text


class AssignmentPublication(TimeStampedModel):
    class StatusChoices(models.TextChoices):
        DRAFT = "draft", "Черновик"
        SCHEDULED = "scheduled", "Запланировано"
        PUBLISHED = "published", "Опубликовано"
        CLOSED = "closed", "Закрыто"
        ARCHIVED = "archived", "Архив"

    assignment = models.ForeignKey(
        "assignments.Assignment",
        on_delete=models.CASCADE,
        related_name="publications",
        verbose_name="Работа",
    )
    course = models.ForeignKey(
        "course.Course",
        on_delete=models.CASCADE,
        related_name="assignment_publications",
        null=True,
        blank=True,
        verbose_name="Курс",
    )
    lesson = models.ForeignKey(
        "course.CourseLesson",
        on_delete=models.CASCADE,
        related_name="assignment_publications",
        null=True,
        blank=True,
        verbose_name="Урок",
    )
    published_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="published_assignments",
        verbose_name="Опубликовал",
    )
    title_override = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Переопределение названия",
    )
    starts_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Доступно с",
    )
    due_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Сдать до",
    )
    available_until = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Доступно до",
    )
    status = models.CharField(
        max_length=32,
        choices=StatusChoices.choices,
        default=StatusChoices.DRAFT,
        verbose_name="Статус публикации",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активно",
    )
    notes = models.TextField(
        blank=True,
        verbose_name="Примечание",
    )

    class Meta:
        db_table = "assignments_assignment_publication"
        verbose_name = "Публикация работы"
        verbose_name_plural = "Публикации работ"
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=("assignment", "status")),
            models.Index(fields=("course", "lesson")),
            models.Index(fields=("starts_at", "due_at")),
        ]

    def clean(self):
        errors: dict[str, str] = {}

        self.title_override = normalize_text(self.title_override)

        if (
            self.lesson_id
            and self.course_id
            and self.lesson.course_id != self.course_id
        ):
            errors["lesson"] = "Урок должен принадлежать выбранному курсу."

        if (
            self.assignment.lesson_id
            and self.lesson_id
            and self.assignment.lesson_id != self.lesson_id
        ):
            errors["lesson"] = (
                "Публикация должна ссылаться на тот же урок, что и работа."
            )

        if (
            self.assignment.course_id
            and self.course_id
            and self.assignment.course_id != self.course_id
        ):
            errors["course"] = (
                "Публикация должна ссылаться на тот же курс, что и работа."
            )

        if self.starts_at and self.due_at and self.starts_at > self.due_at:
            errors["due_at"] = "Срок сдачи не может быть раньше даты начала."

        if self.due_at and self.available_until and self.due_at > self.available_until:
            errors["available_until"] = (
                "Дата окончания доступа не может быть раньше срока сдачи."
            )

        if self.status == self.StatusChoices.ARCHIVED and self.is_active:
            errors["status"] = "Архивная публикация не может быть активной."

        if errors:
            raise ValidationError(errors)

    def __str__(self) -> str:
        return self.title_override or str(self.assignment)
