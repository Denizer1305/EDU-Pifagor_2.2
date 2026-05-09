from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.schedule.constants import BatchStatus, GenerationSource, ImportSourceType
from apps.schedule.models.base import ScheduleTimeStampedModel


class ScheduleGenerationBatch(ScheduleTimeStampedModel):
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="schedule_generation_batches",
        verbose_name=_("Организация"),
    )
    academic_year = models.ForeignKey(
        "education.AcademicYear",
        on_delete=models.CASCADE,
        related_name="schedule_generation_batches",
        verbose_name=_("Учебный год"),
    )
    education_period = models.ForeignKey(
        "education.EducationPeriod",
        on_delete=models.SET_NULL,
        related_name="schedule_generation_batches",
        null=True,
        blank=True,
        verbose_name=_("Учебный период"),
    )
    name = models.CharField(
        _("Название"),
        max_length=255,
    )
    source = models.CharField(
        _("Источник генерации"),
        max_length=32,
        choices=GenerationSource.choices,
        default=GenerationSource.PATTERNS,
        db_index=True,
    )
    status = models.CharField(
        _("Статус"),
        max_length=32,
        choices=BatchStatus.choices,
        default=BatchStatus.PENDING,
        db_index=True,
    )
    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="schedule_generation_batches",
        null=True,
        blank=True,
        verbose_name=_("Кто запустил"),
    )
    started_at = models.DateTimeField(
        _("Дата начала"),
        null=True,
        blank=True,
    )
    finished_at = models.DateTimeField(
        _("Дата завершения"),
        null=True,
        blank=True,
    )
    lessons_created = models.PositiveIntegerField(
        _("Создано занятий"),
        default=0,
    )
    lessons_updated = models.PositiveIntegerField(
        _("Обновлено занятий"),
        default=0,
    )
    conflicts_count = models.PositiveIntegerField(
        _("Количество конфликтов"),
        default=0,
    )
    dry_run = models.BooleanField(
        _("Пробный запуск"),
        default=True,
        db_index=True,
    )
    log = models.TextField(
        _("Лог"),
        blank=True,
    )

    class Meta:
        db_table = "schedule_generation_batches"
        verbose_name = _("Пакет генерации расписания")
        verbose_name_plural = _("Пакеты генерации расписания")
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=("organization", "academic_year", "status")),
            models.Index(fields=("source", "status")),
            models.Index(fields=("dry_run", "created_at")),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.get_status_display()})"


class ScheduleImportBatch(ScheduleTimeStampedModel):
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="schedule_import_batches",
        verbose_name=_("Организация"),
    )
    academic_year = models.ForeignKey(
        "education.AcademicYear",
        on_delete=models.CASCADE,
        related_name="schedule_import_batches",
        verbose_name=_("Учебный год"),
    )
    education_period = models.ForeignKey(
        "education.EducationPeriod",
        on_delete=models.SET_NULL,
        related_name="schedule_import_batches",
        null=True,
        blank=True,
        verbose_name=_("Учебный период"),
    )
    source_file = models.FileField(
        _("Исходный файл"),
        upload_to="schedule/imports/",
        blank=True,
    )
    source_type = models.CharField(
        _("Тип источника"),
        max_length=32,
        choices=ImportSourceType.choices,
        default=ImportSourceType.MANUAL,
        db_index=True,
    )
    status = models.CharField(
        _("Статус"),
        max_length=32,
        choices=BatchStatus.choices,
        default=BatchStatus.PENDING,
        db_index=True,
    )
    imported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="schedule_import_batches",
        null=True,
        blank=True,
        verbose_name=_("Кто импортировал"),
    )
    started_at = models.DateTimeField(
        _("Дата начала"),
        null=True,
        blank=True,
    )
    finished_at = models.DateTimeField(
        _("Дата завершения"),
        null=True,
        blank=True,
    )
    rows_total = models.PositiveIntegerField(
        _("Всего строк"),
        default=0,
    )
    rows_success = models.PositiveIntegerField(
        _("Успешно обработано строк"),
        default=0,
    )
    rows_failed = models.PositiveIntegerField(
        _("Ошибочных строк"),
        default=0,
    )
    log = models.TextField(
        _("Лог"),
        blank=True,
    )

    class Meta:
        db_table = "schedule_import_batches"
        verbose_name = _("Пакет импорта расписания")
        verbose_name_plural = _("Пакеты импорта расписания")
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=("organization", "academic_year", "status")),
            models.Index(fields=("source_type", "status")),
            models.Index(fields=("created_at",)),
        ]

    def __str__(self) -> str:
        return f"{self.get_source_type_display()} — {self.get_status_display()}"
