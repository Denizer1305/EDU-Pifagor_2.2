from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _


class OrganizationType(models.Model):
    """
    Тип образовательной организации.
    Нужен для классификации учебных заведений платформы.
    """

    code = models.CharField(
        _("Код типа организации"),
        max_length=64,
        unique=True,
        db_index=True,
    )
    name = models.CharField(
        _("Название"),
        max_length=255,
        unique=True,
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
        db_table = "organizations_organization_type"
        verbose_name = _("Тип образовательной организации")
        verbose_name_plural = _("Типы образовательных организаций")
        ordering = (
            "name",
        )

    def __str__(self) -> str:
        return self.name
