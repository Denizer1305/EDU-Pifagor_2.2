from __future__ import annotations

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.journal.models import JournalGrade


@admin.register(JournalGrade)
class JournalGradeAdmin(admin.ModelAdmin):
    """Администрирование оценок в журнале."""

    list_display = (
        "id",
        "lesson",
        "student",
        "grade_type",
        "scale",
        "value",
        "weight",
        "is_auto",
        "graded_by",
        "created_at",
    )
    list_filter = (
        "grade_type",
        "scale",
        "is_auto",
        "lesson__course",
        "lesson__group",
        "lesson__date",
    )
    search_fields = (
        "student__email",
        "student__profile__last_name",
        "student__profile__first_name",
        "graded_by__email",
        "graded_by__profile__last_name",
        "graded_by__profile__first_name",
        "lesson__planned_topic",
        "lesson__actual_topic",
        "lesson__course__title",
        "lesson__group__name",
        "comment",
    )
    autocomplete_fields = (
        "lesson",
        "student",
        "graded_by",
        "submission",
        "grade_record",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )
    ordering = (
        "-lesson__date",
        "lesson__lesson_number",
        "student",
        "grade_type",
        "id",
    )
    list_select_related = (
        "lesson",
        "lesson__course",
        "lesson__group",
        "student",
        "graded_by",
        "submission",
        "grade_record",
    )

    fieldsets = (
        (
            _("Основное"),
            {
                "fields": (
                    "lesson",
                    "student",
                    "grade_type",
                    "scale",
                )
            },
        ),
        (
            _("Значение оценки"),
            {
                "fields": (
                    "score_five",
                    "is_passed",
                    "weight",
                    "comment",
                )
            },
        ),
        (
            _("Источник оценки"),
            {
                "fields": (
                    "is_auto",
                    "graded_by",
                    "submission",
                    "grade_record",
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

    @admin.display(description=_("Значение"))
    def value(self, obj: JournalGrade) -> str:
        return obj.display_value
