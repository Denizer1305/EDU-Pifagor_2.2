from __future__ import annotations

from django.db import models

from apps.assignments.models.base import TimeStampedModel, normalize_text


class RubricCriterion(TimeStampedModel):
    class CriterionTypeChoices(models.TextChoices):
        SCORE = "score", "Балльный"
        PASS_FAIL = "pass_fail", "Зачётный"
        TEXT_ONLY = "text_only", "Текстовый"

    rubric = models.ForeignKey(
        "assignments.Rubric",
        on_delete=models.CASCADE,
        related_name="criteria",
        verbose_name="Рубрика",
    )
    title = models.CharField(
        max_length=255,
        verbose_name="Название",
    )
    description = models.TextField(
        blank=True,
        verbose_name="Описание",
    )
    max_score = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
        verbose_name="Максимальный балл",
    )
    order = models.PositiveIntegerField(
        default=1,
        verbose_name="Порядок",
    )
    criterion_type = models.CharField(
        max_length=32,
        choices=CriterionTypeChoices.choices,
        default=CriterionTypeChoices.SCORE,
        verbose_name="Тип критерия",
    )

    class Meta:
        db_table = "assignments_rubric_criterion"
        verbose_name = "Критерий рубрики"
        verbose_name_plural = "Критерии рубрик"
        ordering = ("order", "id")

    def clean(self):
        self.title = normalize_text(self.title)

    def __str__(self) -> str:
        return self.title
