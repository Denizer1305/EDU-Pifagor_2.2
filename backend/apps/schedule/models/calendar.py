from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.schedule.constants import CalendarType, WeekType
from apps.schedule.models.base import ScheduleTimeStampedModel


class ScheduleCalendar(ScheduleTimeStampedModel):
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="schedule_calendars",
        verbose_name=_("Организация"),
    )
    academic_year = models.ForeignKey(
        "education.AcademicYear",
        on_delete=models.CASCADE,
        related_name="schedule_calendars",
        verbose_name=_("Учебный год"),
    )
    education_period = models.ForeignKey(
        "education.EducationPeriod",
        on_delete=models.SET_NULL,
        related_name="schedule_calendars",
        null=True,
        blank=True,
        verbose_name=_("Учебный период"),
    )
    name = models.CharField(
        _("Название"),
        max_length=255,
    )
    calendar_type = models.CharField(
        _("Тип периода"),
        max_length=32,
        choices=CalendarType.choices,
        default=CalendarType.REGULAR,
        db_index=True,
    )
    starts_on = models.DateField(
        _("Дата начала"),
        db_index=True,
    )
    ends_on = models.DateField(
        _("Дата окончания"),
        db_index=True,
    )
    is_active = models.BooleanField(
        _("Активен"),
        default=True,
        db_index=True,
    )
    notes = models.TextField(
        _("Заметки"),
        blank=True,
    )

    class Meta:
        db_table = "schedule_calendars"
        verbose_name = _("Календарь расписания")
        verbose_name_plural = _("Календари расписания")
        ordering = ("organization", "starts_on", "ends_on")
        indexes = [
            models.Index(fields=("organization", "academic_year", "is_active")),
            models.Index(fields=("organization", "calendar_type")),
            models.Index(fields=("starts_on", "ends_on")),
        ]

    def __str__(self) -> str:
        return f"{self.name}: {self.starts_on} — {self.ends_on}"

    def clean(self) -> None:
        super().clean()

        if self.ends_on < self.starts_on:
            raise ValidationError(
                {"ends_on": _("Дата окончания не может быть раньше даты начала.")}
            )


class ScheduleWeekTemplate(ScheduleTimeStampedModel):
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="schedule_week_templates",
        verbose_name=_("Организация"),
    )
    academic_year = models.ForeignKey(
        "education.AcademicYear",
        on_delete=models.CASCADE,
        related_name="schedule_week_templates",
        verbose_name=_("Учебный год"),
    )
    education_period = models.ForeignKey(
        "education.EducationPeriod",
        on_delete=models.SET_NULL,
        related_name="schedule_week_templates",
        null=True,
        blank=True,
        verbose_name=_("Учебный период"),
    )
    name = models.CharField(
        _("Название"),
        max_length=255,
    )
    week_type = models.CharField(
        _("Тип недели"),
        max_length=32,
        choices=WeekType.choices,
        default=WeekType.EVERY,
        db_index=True,
    )
    starts_on = models.DateField(
        _("Дата начала"),
        null=True,
        blank=True,
    )
    ends_on = models.DateField(
        _("Дата окончания"),
        null=True,
        blank=True,
    )
    is_default = models.BooleanField(
        _("По умолчанию"),
        default=False,
        db_index=True,
    )
    is_active = models.BooleanField(
        _("Активен"),
        default=True,
        db_index=True,
    )
    notes = models.TextField(
        _("Заметки"),
        blank=True,
    )

    class Meta:
        db_table = "schedule_week_templates"
        verbose_name = _("Шаблон учебной недели")
        verbose_name_plural = _("Шаблоны учебных недель")
        ordering = ("organization", "academic_year", "week_type", "name")
        indexes = [
            models.Index(fields=("organization", "academic_year", "is_active")),
            models.Index(fields=("organization", "week_type")),
            models.Index(fields=("organization", "is_default")),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.get_week_type_display()})"

    def clean(self) -> None:
        super().clean()

        if self.starts_on and self.ends_on and self.ends_on < self.starts_on:
            raise ValidationError(
                {"ends_on": _("Дата окончания не может быть раньше даты начала.")}
            )
