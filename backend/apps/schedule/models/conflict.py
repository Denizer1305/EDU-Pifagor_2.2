from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.schedule.constants import ConflictSeverity, ConflictStatus, ConflictType
from apps.schedule.models.base import ScheduleTimeStampedModel


class ScheduleConflict(ScheduleTimeStampedModel):
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="schedule_conflicts",
        verbose_name=_("Организация"),
    )
    conflict_type = models.CharField(
        _("Тип конфликта"),
        max_length=64,
        choices=ConflictType.choices,
        db_index=True,
    )
    severity = models.CharField(
        _("Критичность"),
        max_length=32,
        choices=ConflictSeverity.choices,
        default=ConflictSeverity.WARNING,
        db_index=True,
    )
    status = models.CharField(
        _("Статус"),
        max_length=32,
        choices=ConflictStatus.choices,
        default=ConflictStatus.OPEN,
        db_index=True,
    )
    lesson = models.ForeignKey(
        "schedule.ScheduledLesson",
        on_delete=models.CASCADE,
        related_name="conflicts",
        null=True,
        blank=True,
        verbose_name=_("Занятие"),
    )
    pattern = models.ForeignKey(
        "schedule.SchedulePattern",
        on_delete=models.CASCADE,
        related_name="conflicts",
        null=True,
        blank=True,
        verbose_name=_("Шаблон"),
    )
    related_lesson = models.ForeignKey(
        "schedule.ScheduledLesson",
        on_delete=models.CASCADE,
        related_name="related_conflicts",
        null=True,
        blank=True,
        verbose_name=_("Связанное занятие"),
    )
    related_pattern = models.ForeignKey(
        "schedule.SchedulePattern",
        on_delete=models.CASCADE,
        related_name="related_conflicts",
        null=True,
        blank=True,
        verbose_name=_("Связанный шаблон"),
    )
    teacher = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        related_name="schedule_conflicts_as_teacher",
        null=True,
        blank=True,
        verbose_name=_("Преподаватель"),
    )
    room = models.ForeignKey(
        "schedule.ScheduleRoom",
        on_delete=models.SET_NULL,
        related_name="conflicts",
        null=True,
        blank=True,
        verbose_name=_("Аудитория"),
    )
    group = models.ForeignKey(
        "organizations.Group",
        on_delete=models.SET_NULL,
        related_name="schedule_conflicts",
        null=True,
        blank=True,
        verbose_name=_("Группа"),
    )
    date = models.DateField(
        _("Дата"),
        null=True,
        blank=True,
        db_index=True,
    )
    starts_at = models.TimeField(
        _("Время начала"),
        null=True,
        blank=True,
    )
    ends_at = models.TimeField(
        _("Время окончания"),
        null=True,
        blank=True,
    )
    message = models.TextField(
        _("Сообщение"),
    )
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="resolved_schedule_conflicts",
        null=True,
        blank=True,
        verbose_name=_("Кто решил"),
    )
    resolved_at = models.DateTimeField(
        _("Дата решения"),
        null=True,
        blank=True,
    )
    notes = models.TextField(
        _("Заметки"),
        blank=True,
    )

    class Meta:
        db_table = "schedule_conflicts"
        verbose_name = _("Конфликт расписания")
        verbose_name_plural = _("Конфликты расписания")
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=("organization", "status")),
            models.Index(fields=("conflict_type", "severity")),
            models.Index(fields=("date", "starts_at", "ends_at")),
            models.Index(fields=("teacher", "date")),
            models.Index(fields=("room", "date")),
            models.Index(fields=("group", "date")),
        ]

    def __str__(self) -> str:
        return f"{self.get_conflict_type_display()}: {self.message[:80]}"

    def mark_resolved(self, user=None) -> None:
        self.status = ConflictStatus.RESOLVED
        self.resolved_by = user
        self.resolved_at = timezone.now()
