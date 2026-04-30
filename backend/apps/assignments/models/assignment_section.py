from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import models

from apps.assignments.models.base import TimeStampedModel, normalize_text


class AssignmentSection(TimeStampedModel):
    class SectionTypeChoices(models.TextChoices):
        COMMON = "common", "Общая часть"
        PART_A = "part_a", "Часть A"
        PART_B = "part_b", "Часть B"
        PART_C = "part_c", "Часть C"
        PRACTICAL = "practical", "Практическая часть"
        ORAL = "oral", "Устная часть"
        WRITTEN = "written", "Письменная часть"
        THEORY = "theory", "Теоретическая часть"

    assignment = models.ForeignKey(
        "assignments.Assignment",
        on_delete=models.CASCADE,
        related_name="sections",
        verbose_name="Работа",
    )
    variant = models.ForeignKey(
        "assignments.AssignmentVariant",
        on_delete=models.CASCADE,
        related_name="sections",
        null=True,
        blank=True,
        verbose_name="Вариант",
    )
    title = models.CharField(
        max_length=255,
        verbose_name="Название секции",
    )
    description = models.TextField(
        blank=True,
        verbose_name="Описание",
    )
    section_type = models.CharField(
        max_length=32,
        choices=SectionTypeChoices.choices,
        default=SectionTypeChoices.COMMON,
        verbose_name="Тип секции",
    )
    order = models.PositiveIntegerField(
        default=1,
        verbose_name="Порядок",
    )
    max_score = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
        verbose_name="Максимальный балл",
    )
    is_required = models.BooleanField(
        default=True,
        verbose_name="Обязательная",
    )

    class Meta:
        db_table = "assignments_assignment_section"
        verbose_name = "Секция работы"
        verbose_name_plural = "Секции работ"
        ordering = ("order", "id")
        indexes = [
            models.Index(fields=("assignment", "variant")),
            models.Index(fields=("section_type",)),
        ]

    def clean(self):
        errors: dict[str, str] = {}

        self.title = normalize_text(self.title)
        if not self.title:
            errors["title"] = "Название секции обязательно."

        if self.variant_id and self.variant.assignment_id != self.assignment_id:
            errors["variant"] = "Вариант должен принадлежать выбранной работе."

        if errors:
            raise ValidationError(errors)

    def __str__(self) -> str:
        return self.title
