from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.schedule.constants import ScheduleChangeType
from apps.schedule.models.base import ScheduleTimeStampedModel


class ScheduleChange(ScheduleTimeStampedModel):
    scheduled_lesson = models.ForeignKey(
        "schedule.ScheduledLesson",
        on_delete=models.CASCADE,
        related_name="changes",
        verbose_name=_("Занятие расписания"),
    )
    change_type = models.CharField(
        _("Тип изменения"),
        max_length=32,
        choices=ScheduleChangeType.choices,
        db_index=True,
    )
    old_date = models.DateField(
        _("Старая дата"),
        null=True,
        blank=True,
    )
    new_date = models.DateField(
        _("Новая дата"),
        null=True,
        blank=True,
    )
    old_time_slot = models.ForeignKey(
        "schedule.ScheduleTimeSlot",
        on_delete=models.SET_NULL,
        related_name="old_schedule_changes",
        null=True,
        blank=True,
        verbose_name=_("Старый временной слот"),
    )
    new_time_slot = models.ForeignKey(
        "schedule.ScheduleTimeSlot",
        on_delete=models.SET_NULL,
        related_name="new_schedule_changes",
        null=True,
        blank=True,
        verbose_name=_("Новый временной слот"),
    )
    old_starts_at = models.TimeField(
        _("Старое время начала"),
        null=True,
        blank=True,
    )
    new_starts_at = models.TimeField(
        _("Новое время начала"),
        null=True,
        blank=True,
    )
    old_ends_at = models.TimeField(
        _("Старое время окончания"),
        null=True,
        blank=True,
    )
    new_ends_at = models.TimeField(
        _("Новое время окончания"),
        null=True,
        blank=True,
    )
    old_room = models.ForeignKey(
        "schedule.ScheduleRoom",
        on_delete=models.SET_NULL,
        related_name="old_schedule_changes",
        null=True,
        blank=True,
        verbose_name=_("Старая аудитория"),
    )
    new_room = models.ForeignKey(
        "schedule.ScheduleRoom",
        on_delete=models.SET_NULL,
        related_name="new_schedule_changes",
        null=True,
        blank=True,
        verbose_name=_("Новая аудитория"),
    )
    old_teacher = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        related_name="old_schedule_changes_as_teacher",
        null=True,
        blank=True,
        verbose_name=_("Старый преподаватель"),
    )
    new_teacher = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        related_name="new_schedule_changes_as_teacher",
        null=True,
        blank=True,
        verbose_name=_("Новый преподаватель"),
    )
    reason = models.CharField(
        _("Причина"),
        max_length=255,
        blank=True,
    )
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="schedule_changes",
        null=True,
        blank=True,
        verbose_name=_("Кто изменил"),
    )
    comment = models.TextField(
        _("Комментарий"),
        blank=True,
    )

    class Meta:
        db_table = "schedule_changes"
        verbose_name = _("Изменение расписания")
        verbose_name_plural = _("Изменения расписания")
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=("scheduled_lesson", "change_type")),
            models.Index(fields=("change_type", "created_at")),
            models.Index(fields=("changed_by", "created_at")),
        ]

    def __str__(self) -> str:
        return f"{self.scheduled_lesson_id}: {self.get_change_type_display()}"
