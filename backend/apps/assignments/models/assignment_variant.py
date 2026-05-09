from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import models

from apps.assignments.models.base import TimeStampedModel, normalize_text


class AssignmentVariant(TimeStampedModel):
    assignment = models.ForeignKey(
        "assignments.Assignment",
        on_delete=models.CASCADE,
        related_name="variants",
        verbose_name="Работа",
    )
    title = models.CharField(
        max_length=255,
        verbose_name="Название варианта",
    )
    code = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Код варианта",
    )
    description = models.TextField(
        blank=True,
        verbose_name="Описание",
    )
    variant_number = models.PositiveIntegerField(
        verbose_name="Номер варианта",
    )
    order = models.PositiveIntegerField(
        default=1,
        verbose_name="Порядок",
    )
    is_default = models.BooleanField(
        default=False,
        verbose_name="По умолчанию",
    )
    max_score = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
        verbose_name="Максимальный балл",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активен",
    )

    class Meta:
        db_table = "assignments_assignment_variant"
        verbose_name = "Вариант работы"
        verbose_name_plural = "Варианты работ"
        ordering = ("order", "variant_number", "id")
        constraints = [
            models.UniqueConstraint(
                fields=("assignment", "variant_number"),
                name="uniq_assignment_variant_number",
            ),
            models.UniqueConstraint(
                fields=("assignment", "order"),
                name="uniq_assignment_variant_order",
            ),
        ]

    def clean(self):
        self.title = normalize_text(self.title)
        self.code = normalize_text(self.code)

        if not self.title:
            raise ValidationError({"title": "Название варианта обязательно."})

    def __str__(self) -> str:
        return f"{self.assignment} — {self.title}"
