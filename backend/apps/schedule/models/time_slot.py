from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.schedule.constants import EducationLevel
from apps.schedule.models.base import ScheduleTimeStampedModel


class ScheduleTimeSlot(ScheduleTimeStampedModel):
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="schedule_time_slots",
        verbose_name=_("Организация"),
    )
    name = models.CharField(
        _("Название"),
        max_length=128,
    )
    number = models.PositiveSmallIntegerField(
        _("Номер занятия"),
        db_index=True,
    )
    starts_at = models.TimeField(
        _("Время начала"),
    )
    ends_at = models.TimeField(
        _("Время окончания"),
    )
    duration_minutes = models.PositiveSmallIntegerField(
        _("Длительность в минутах"),
        default=45,
    )
    education_level = models.CharField(
        _("Уровень образования"),
        max_length=32,
        choices=EducationLevel.choices,
        default=EducationLevel.MIXED,
        db_index=True,
    )
    is_pair = models.BooleanField(
        _("Пара"),
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
        db_table = "schedule_time_slots"
        verbose_name = _("Временной слот")
        verbose_name_plural = _("Временные слоты")
        ordering = ("organization", "number", "starts_at")
        indexes = [
            models.Index(fields=("organization", "is_active")),
            models.Index(fields=("organization", "number")),
            models.Index(fields=("organization", "education_level")),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=("organization", "number", "education_level"),
                name="schedule_time_slot_unique_org_number_level",
            )
        ]

    def __str__(self) -> str:
        return f"{self.number}. {self.starts_at}–{self.ends_at}"

    def clean(self) -> None:
        super().clean()

        if self.ends_at <= self.starts_at:
            raise ValidationError(
                {"ends_at": _("Время окончания должно быть позже времени начала.")}
            )
