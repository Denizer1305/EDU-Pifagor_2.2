from __future__ import annotations

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.schedule.models import ScheduleGenerationBatch, ScheduleImportBatch


@admin.register(ScheduleGenerationBatch)
class ScheduleGenerationBatchAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "organization",
        "academic_year",
        "education_period",
        "source",
        "status",
        "dry_run",
        "lessons_created",
        "lessons_updated",
        "conflicts_count",
        "started_at",
        "finished_at",
    )
    list_filter = (
        "status",
        "source",
        "dry_run",
        "organization",
        "academic_year",
        "education_period",
    )
    search_fields = (
        "name",
        "log",
        "organization__name",
        "academic_year__name",
        "education_period__name",
    )
    ordering = ("-created_at",)
    list_select_related = (
        "organization",
        "academic_year",
        "education_period",
        "generated_by",
    )
    autocomplete_fields = (
        "organization",
        "academic_year",
        "education_period",
        "generated_by",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "organization",
                    "academic_year",
                    "education_period",
                    "name",
                    "source",
                    "status",
                    "dry_run",
                    "generated_by",
                )
            },
        ),
        (
            _("Выполнение"),
            {
                "fields": (
                    "started_at",
                    "finished_at",
                    "lessons_created",
                    "lessons_updated",
                    "conflicts_count",
                )
            },
        ),
        (
            _("Лог"),
            {
                "fields": (
                    "log",
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )


@admin.register(ScheduleImportBatch)
class ScheduleImportBatchAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "organization",
        "academic_year",
        "education_period",
        "source_type",
        "status",
        "rows_total",
        "rows_success",
        "rows_failed",
        "started_at",
        "finished_at",
    )
    list_filter = (
        "status",
        "source_type",
        "organization",
        "academic_year",
        "education_period",
    )
    search_fields = (
        "log",
        "organization__name",
        "academic_year__name",
        "education_period__name",
    )
    ordering = ("-created_at",)
    list_select_related = (
        "organization",
        "academic_year",
        "education_period",
        "imported_by",
    )
    autocomplete_fields = (
        "organization",
        "academic_year",
        "education_period",
        "imported_by",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "organization",
                    "academic_year",
                    "education_period",
                    "source_file",
                    "source_type",
                    "status",
                    "imported_by",
                )
            },
        ),
        (
            _("Выполнение"),
            {
                "fields": (
                    "started_at",
                    "finished_at",
                    "rows_total",
                    "rows_success",
                    "rows_failed",
                )
            },
        ),
        (
            _("Лог"),
            {
                "fields": (
                    "log",
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )
