from __future__ import annotations

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.journal.models import AttendanceRecord


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    """Администрирование записей посещаемости."""

    list_display = (
        "id",
        "lesson",
        "student",
        "status",
        "comment_short",
        "created_at",
    )
    list_filter = (
        "status",
        "lesson__date",
        "lesson__course",
        "lesson__group",
    )
    search_fields = (
        "student__email",
        "student__profile__last_name",
        "student__profile__first_name",
        "lesson__planned_topic",
        "lesson__actual_topic",
        "lesson__course__title",
        "lesson__course__code",
        "lesson__group__name",
        "lesson__group__code",
    )
    autocomplete_fields = (
        "lesson",
        "student",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )
    ordering = (
        "-lesson__date",
        "lesson__lesson_number",
        "student",
    )
    list_select_related = (
        "lesson",
        "lesson__course",
        "lesson__group",
        "student",
    )

    fieldsets = (
        (
            _("Основное"),
            {
                "fields": (
                    "lesson",
                    "student",
                    "status",
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

    @admin.display(description=_("Комментарий"))
    def comment_short(self, obj: AttendanceRecord) -> str:
        if not obj.comment:
            return "—"

        if len(obj.comment) <= 80:
            return obj.comment

        return f"{obj.comment[:80]}..."
