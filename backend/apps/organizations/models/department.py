from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _


class Department(models.Model):
    """
    Подразделение образовательной организации.
    Используется для факультетов, отделений, кафедр и иных внутренних единиц.
    """

    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="departments",
        verbose_name=_("Организация"),
    )

    name = models.CharField(
        _("Название подразделения"),
        max_length=255,
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
        _("Активно"),
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
        db_table = "organizations_department"
        verbose_name = _("Подразделение")
        verbose_name_plural = _("Подразделения")
        ordering = (
            "organization",
            "name",
        )
        constraints = [
            models.UniqueConstraint(
                fields=(
                    "organization",
                    "name",
                ),
                name="unique_department_name_per_organization",
            )
        ]

    def __str__(self) -> str:
        return f"{self.organization} — {self.short_name or self.name}"
