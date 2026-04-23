from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class Curriculum(models.Model):
    """
    Учебный план.
    Определяет академическую структуру подготовки для организации
    или ее подразделения в рамках конкретного учебного года.
    """

    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="curricula",
        verbose_name=_("Организация"),
    )
    department = models.ForeignKey(
        "organizations.Department",
        on_delete=models.SET_NULL,
        related_name="curricula",
        verbose_name=_("Подразделение"),
        blank=True,
        null=True,
    )
    academic_year = models.ForeignKey(
        "education.AcademicYear",
        on_delete=models.PROTECT,
        related_name="curricula",
        verbose_name=_("Учебный год"),
    )

    code = models.CharField(
        _("Код учебного плана"),
        max_length=64,
    )
    name = models.CharField(
        _("Название учебного плана"),
        max_length=255,
    )

    description = models.TextField(
        _("Описание"),
        blank=True,
    )

    total_hours = models.PositiveIntegerField(
        _("Общее количество часов"),
        blank=True,
        null=True,
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
        db_table = "education_curriculum"
        verbose_name = _("Учебный план")
        verbose_name_plural = _("Учебные планы")
        ordering = ("organization", "name")
        constraints = [
            models.UniqueConstraint(
                fields=("organization", "academic_year", "code"),
                name="unique_curriculum_code_per_organization_and_year",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.organization} — {self.name}"

    def clean(self) -> None:
        super().clean()

        if self.department and self.department.organization_id != self.organization_id:
            raise ValidationError(
                {"department": _("Подразделение должно принадлежать той же организации, что и учебный план.")}
            )
