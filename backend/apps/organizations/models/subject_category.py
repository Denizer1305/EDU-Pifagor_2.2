from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _


class SubjectCategory(models.Model):
    """
    Категория учебных предметов.
    Используется для группировки дисциплин по направлениям.
    """

    code = models.CharField(
        _("Код категории"),
        max_length=64,
        unique=True,
        db_index=True,
    )
    name = models.CharField(
        _("Название категории"),
        max_length=255,
        unique=True,
    )
    description = models.TextField(
        _("Описание"),
        blank=True,
    )

    is_active = models.BooleanField(
        _("Активна"),
        default=True,
    )

    created_at = models.DateTimeField(
        _("Дата создания"),
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        _("Дата обновления"),
        auto_now=True,
    )

    class Meta:
        db_table = "organizations_subject_category"
        verbose_name = _("Категория предметов")
        verbose_name_plural = _("Категории предметов")
        ordering = (
            "name",
        )

    def __str__(self) -> str:
        return self.name
