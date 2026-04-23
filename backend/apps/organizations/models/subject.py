from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _


class Subject(models.Model):
    """
    Учебный предмет.
    Представляет конкретную дисциплину, которая используется в курсах и учебных группах.
    """

    category = models.ForeignKey(
        "organizations.SubjectCategory",
        on_delete=models.PROTECT,
        related_name="subjects",
        verbose_name=_("Категория"),
    )

    name = models.CharField(
        _("Название предмета"),
        max_length=255,
        unique=True,
    )
    short_name = models.CharField(
        _("Краткое название"),
        max_length=255,
        blank=True,
    )
    description = models.TextField(
        _("Описание"),
        blank=True,
    )

    is_active = models.BooleanField(
        _("Активен"),
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
        db_table = "organizations_subject"
        verbose_name = _("Учебный предмет")
        verbose_name_plural = _("Учебные предметы")
        ordering = (
            "name",
        )

    def __str__(self) -> str:
        return self.short_name or self.name
