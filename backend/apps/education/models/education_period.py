from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from apps.education.validators import validate_period_code


class EducationPeriod(models.Model):
    """
    Учебный период.
    Используется для семестров, триместров, четвертей, модулей
    и иных интервалов внутри учебного года.
    """

    class PeriodTypeChoices(models.TextChoices):
        YEAR = "year", _("Год")
        SEMESTER = "semester", _("Семестр")
        TRIMESTER = "trimester", _("Триместр")
        QUARTER = "quarter", _("Четверть")
        MODULE = "module", _("Модуль")
        OTHER = "other", _("Иной")

    academic_year = models.ForeignKey(
        "education.AcademicYear",
        on_delete=models.CASCADE,
        related_name="periods",
        verbose_name=_("Учебный год"),
    )

    name = models.CharField(
        _("Название периода"),
        max_length=255,
    )
    code = models.CharField(
        _("Код периода"),
        max_length=64,
        validators=[validate_period_code]
    )
    period_type = models.CharField(
        _("Тип периода"),
        max_length=32,
        choices=PeriodTypeChoices.choices,
        default=PeriodTypeChoices.SEMESTER,
    )
    sequence = models.PositiveSmallIntegerField(
        _("Порядковый номер"),
        default=1,
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
        _("Текущий период"),
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
        db_table = "education_period"
        verbose_name = _("Учебный период")
        verbose_name_plural = _("Учебные периоды")
        ordering = ("academic_year", "sequence")
        constraints = [
            models.UniqueConstraint(
                fields=("academic_year", "code"),
                name="unique_period_code_per_academic_year",
            ),
            models.UniqueConstraint(
                fields=("academic_year", "sequence"),
                name="unique_period_sequence_per_academic_year",
            ),
            models.UniqueConstraint(
                fields=("academic_year", "is_current"),
                condition=Q(is_current=True),
                name="unique_current_period_per_academic_year",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.academic_year} — {self.name}"

    def clean(self) -> None:
        super().clean()

        if self.end_date <= self.start_date:
            raise ValidationError(
                {"end_date": _("Дата окончания должна быть позже даты начала.")}
            )

        if self.start_date < self.academic_year.start_date:
            raise ValidationError(
                {"start_date": _("Период не может начинаться раньше учебного года.")}
            )

        if self.end_date > self.academic_year.end_date:
            raise ValidationError(
                {"end_date": _("Период не может заканчиваться позже учебного года.")}
            )
