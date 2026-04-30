from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import models

from apps.course.models.base import OrderedModel, TimeStampedModel, normalize_text


class CourseModule(TimeStampedModel, OrderedModel):
    class Meta:
        db_table = "course_module"
        verbose_name = "Модуль курса"
        verbose_name_plural = "Модули курса"
        ordering = ("course", "order", "id")
        constraints = [
            models.UniqueConstraint(
                fields=("course", "order"),
                name="unique_course_module_order",
            ),
        ]

    course = models.ForeignKey(
        "course.Course",
        on_delete=models.CASCADE,
        related_name="modules",
        verbose_name="Курс",
    )
    title = models.CharField(
        max_length=255,
        verbose_name="Название",
    )
    description = models.TextField(
        blank=True,
        verbose_name="Описание",
    )
    is_required = models.BooleanField(
        default=True,
        verbose_name="Обязательный",
    )
    is_published = models.BooleanField(
        default=True,
        verbose_name="Опубликован",
    )
    estimated_minutes = models.PositiveIntegerField(
        default=0,
        verbose_name="Плановая длительность (мин)",
    )

    def clean(self):
        errors = {}

        self.title = normalize_text(self.title)
        self.description = normalize_text(self.description)

        if self.order < 1:
            errors["order"] = "Порядок модуля должен быть больше нуля."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.title = normalize_text(self.title)
        self.description = normalize_text(self.description)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.title
