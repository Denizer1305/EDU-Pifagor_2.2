from __future__ import annotations

from django.contrib import admin
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.schedule.constants import ConflictStatus
from apps.schedule.models import ScheduleConflict


@admin.register(ScheduleConflict)
class ScheduleConflictAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "conflict_type",
        "severity",
        "status",
        "organization",
        "date",
        "starts_at",
        "ends_at",
        "teacher",
        "room",
        "group",
        "message_short",
        "created_at",
    )
    list_filter = (
        "status",
        "severity",
        "conflict_type",
        "organization",
        "date",
    )
    search_fields = (
        "message",
        "notes",
        "teacher__email",
        "teacher__profile__last_name",
        "teacher__profile__first_name",
        "room__name",
        "room__number",
        "group__name",
    )
    date_hierarchy = "date"
    ordering = ("-created_at",)
    list_select_related = (
        "organization",
        "lesson",
        "pattern",
        "related_lesson",
        "related_pattern",
        "teacher",
        "room",
        "group",
        "resolved_by",
    )
    autocomplete_fields = (
        "organization",
        "lesson",
        "pattern",
        "related_lesson",
        "related_pattern",
        "teacher",
        "room",
        "group",
        "resolved_by",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )
    actions = (
        "mark_as_resolved",
        "mark_as_ignored",
        "reopen_conflicts",
    )
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "organization",
                    "conflict_type",
                    "severity",
                    "status",
                    "message",
                )
            },
        ),
        (
            _("Объекты конфликта"),
            {
                "fields": (
                    "lesson",
                    "pattern",
                    "related_lesson",
                    "related_pattern",
                )
            },
        ),
        (
            _("Участники и время"),
            {
                "fields": (
                    "teacher",
                    "room",
                    "group",
                    "date",
                    "starts_at",
                    "ends_at",
                )
            },
        ),
        (
            _("Решение"),
            {
                "fields": (
                    "resolved_by",
                    "resolved_at",
                    "notes",
                )
            },
        ),
        (
            _("Служебная информация"),
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )

    @admin.display(description=_("Сообщение"))
    def message_short(self, obj: ScheduleConflict) -> str:
        if len(obj.message) <= 80:
            return obj.message
        return f"{obj.message[:80]}..."

    @admin.action(description=_("Отметить как решённые"))
    def mark_as_resolved(self, request, queryset):
        queryset.update(
            status=ConflictStatus.RESOLVED,
            resolved_by=request.user,
            resolved_at=timezone.now(),
        )

    @admin.action(description=_("Игнорировать"))
    def mark_as_ignored(self, request, queryset):
        queryset.update(
            status=ConflictStatus.IGNORED,
            resolved_by=request.user,
            resolved_at=timezone.now(),
        )

    @admin.action(description=_("Переоткрыть"))
    def reopen_conflicts(self, request, queryset):
        queryset.update(
            status=ConflictStatus.OPEN,
            resolved_by=None,
            resolved_at=None,
        )
