from __future__ import annotations

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.journal.models import TopicProgress


@admin.register(TopicProgress)
class TopicProgressAdmin(admin.ModelAdmin):
    """Администрирование прогресса прохождения тем."""

    list_display = (
        "id",
        "course",
        "group",
        "lesson",
        "journal_lesson",
        "planned_date",
        "actual_date",
        "status",
        "days_behind",
        "is_behind_display",
    )
    list_filter = (
        "status",
        "course",
        "group",
    )
    search_fields = (
        "lesson__title",
        "course__title",
        "course__code",
        "group__name",
        "group__code",
        "journal_lesson__planned_topic",
        "journal_lesson__actual_topic",
    )
    autocomplete_fields = (
        "course",
        "group",
        "lesson",
        "journal_lesson",
    )
    readonly_fields = (
        "days_behind",
        "created_at",
        "updated_at",
    )
    ordering = (
        "planned_date",
        "course",
        "group",
    )
    list_select_related = (
        "course",
        "group",
        "lesson",
        "journal_lesson",
    )

    fieldsets = (
        (
            _("Связи"),
            {
                "fields": (
                    "course",
                    "group",
                    "lesson",
                    "journal_lesson",
                )
            },
        ),
        (
            _("Даты и статус"),
            {
                "fields": (
                    "planned_date",
                    "actual_date",
                    "status",
                    "days_behind",
                    "comment",
                )
            },
        ),
        (
            _("Служебная информация"),
            {
                "classes": ("collapse",),
                "fields": (
                    "created_at",
                    "updated_at",
                ),
            },
        ),
    )

    @admin.display(description=_("Отстаёт?"), boolean=True)
    def is_behind_display(self, obj: TopicProgress) -> bool:
        return obj.is_behind
