from __future__ import annotations

from django.contrib import admin
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from apps.journal.models import JournalSummary


@admin.register(JournalSummary)
class JournalSummaryAdmin(admin.ModelAdmin):
    """Администрирование кэша сводок журнала. Только просмотр."""

    list_display = (
        "id",
        "course",
        "group",
        "student",
        "attendance_percent",
        "avg_score",
        "progress_percent",
        "debt_count",
        "calculated_at",
    )
    list_filter = (
        "course",
        "group",
        "calculated_at",
    )
    search_fields = (
        "student__email",
        "student__profile__last_name",
        "student__profile__first_name",
        "group__name",
        "group__code",
        "course__title",
        "course__code",
    )
    readonly_fields = (
        "course",
        "group",
        "student",
        "total_lessons",
        "attended_lessons",
        "absent_lessons",
        "attendance_percent",
        "avg_score",
        "debt_count",
        "total_topics",
        "completed_topics",
        "topics_behind",
        "progress_percent",
        "calculated_at",
    )
    ordering = ("-calculated_at",)
    list_select_related = (
        "course",
        "group",
        "student",
    )

    fieldsets = (
        (
            _("Связи"),
            {
                "fields": (
                    "course",
                    "group",
                    "student",
                )
            },
        ),
        (
            _("Посещаемость"),
            {
                "fields": (
                    "total_lessons",
                    "attended_lessons",
                    "absent_lessons",
                    "attendance_percent",
                )
            },
        ),
        (
            _("Оценки и долги"),
            {
                "fields": (
                    "avg_score",
                    "debt_count",
                )
            },
        ),
        (
            _("Прогресс по темам"),
            {
                "fields": (
                    "total_topics",
                    "completed_topics",
                    "topics_behind",
                    "progress_percent",
                )
            },
        ),
        (
            _("Служебная информация"),
            {
                "fields": ("calculated_at",),
            },
        ),
    )

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_change_permission(
        self,
        request: HttpRequest,
        obj: JournalSummary | None = None,
    ) -> bool:
        return False

    def has_delete_permission(
        self,
        request: HttpRequest,
        obj: JournalSummary | None = None,
    ) -> bool:
        return False
