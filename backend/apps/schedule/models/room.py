from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.schedule.constants import RoomType
from apps.schedule.models.base import ScheduleTimeStampedModel


class ScheduleRoom(ScheduleTimeStampedModel):
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="schedule_rooms",
        verbose_name=_("Организация"),
    )
    department = models.ForeignKey(
        "organizations.Department",
        on_delete=models.SET_NULL,
        related_name="schedule_rooms",
        null=True,
        blank=True,
        verbose_name=_("Отделение"),
    )
    name = models.CharField(
        _("Название"),
        max_length=255,
    )
    number = models.CharField(
        _("Номер аудитории"),
        max_length=64,
        blank=True,
        db_index=True,
    )
    room_type = models.CharField(
        _("Тип аудитории"),
        max_length=32,
        choices=RoomType.choices,
        default=RoomType.CLASSROOM,
        db_index=True,
    )
    capacity = models.PositiveSmallIntegerField(
        _("Вместимость"),
        default=0,
    )
    floor = models.CharField(
        _("Этаж"),
        max_length=32,
        blank=True,
    )
    building = models.CharField(
        _("Корпус"),
        max_length=128,
        blank=True,
    )
    is_active = models.BooleanField(
        _("Активна"),
        default=True,
        db_index=True,
    )
    notes = models.TextField(
        _("Заметки"),
        blank=True,
    )

    class Meta:
        db_table = "schedule_rooms"
        verbose_name = _("Аудитория расписания")
        verbose_name_plural = _("Аудитории расписания")
        ordering = ("organization", "building", "number", "name")
        indexes = [
            models.Index(fields=("organization", "is_active")),
            models.Index(fields=("organization", "room_type")),
            models.Index(fields=("organization", "number")),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=("organization", "number", "building"),
                name="schedule_room_unique_org_number_building",
            )
        ]

    def __str__(self) -> str:
        if self.number:
            return self.number
        return self.name
