from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from apps.education.validators import validate_academic_year_name


class AcademicYear(models.Model):
    """
    Учебный год.
    Используется как базовая академическая сущность для учебной нагрузки,
    зачислений, предметов, расписания и аналитики.
    """

    name = models.CharField(
        _("Наименование учебного года"),
        max_length=32,
        unique=True,
        help_text=_("Например: 2025/2026"),
        validators=[validate_academic_year_name]
    )
    start_date = models.DateField(
        _("Дата начала"),
    )
    end_date = models.DateField(
        _("Дата окончания"),
    )

    description = models.TextField(
        _("Описание"),
        blank=True,
    )

    is_current = models.BooleanField(
        _("Текущий учебный год"),
        default=False,
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
        db_table = "education_academic_year"
        verbose_name = _("Учебный год")
        verbose_name_plural = _("Учебные годы")
        ordering = ("-start_date",)
        constraints = [
            models.UniqueConstraint(
                fields=("is_current",),
                condition=Q(is_current=True),
                name="unique_current_academic_year",
            ),
        ]

    def __str__(self) -> str:
        return self.name

    def clean(self) -> None:
        super().clean()

        if self.end_date <= self.start_date:
            raise ValidationError(
                {"end_date": _("Дата окончания должна быть позже даты начала.")}
            )
