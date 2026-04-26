from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.assignments.models.base import TimeStampedModel, normalize_text


class Rubric(TimeStampedModel):
    title = models.CharField(
        max_length=255,
        verbose_name="Название",
    )
    description = models.TextField(
        blank=True,
        verbose_name="Описание",
    )
    assignment_kind = models.CharField(
        max_length=64,
        blank=True,
        verbose_name="Тип работы",
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.SET_NULL,
        related_name="rubrics",
        null=True,
        blank=True,
        verbose_name="Организация",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="rubrics",
        null=True,
        blank=True,
        verbose_name="Автор",
    )
    is_template = models.BooleanField(
        default=True,
        verbose_name="Шаблон",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активна",
    )

    class Meta:
        db_table = "assignments_rubric"
        verbose_name = "Рубрика"
        verbose_name_plural = "Рубрики"
        ordering = ("title",)

    def clean(self):
        self.title = normalize_text(self.title)

    def __str__(self) -> str:
        return self.title
