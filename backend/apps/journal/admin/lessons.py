from __future__ import annotations

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.journal.admin.inlines import AttendanceInline, GradeInline
from apps.journal.models import JournalLesson


@admin.register(JournalLesson)
class JournalLessonAdmin(admin.ModelAdmin):
    """Администрирование занятий журнала."""

    list_display = (
        "id",
        "date",
        "lesson_number",
        "course",
        "group",
        "teacher",
        "status",
        "topic",
    )
    list_filter = (
        "status",
        "date",
        "course",
        "group",
        "teacher",
    )
    search_fields = (
        "planned_topic",
        "actual_topic",
        "homework",
        "teacher__email",
        "teacher__profile__last_name",
        "teacher__profile__first_name",
        "group__name",
        "group__code",
        "course__title",
        "course__code",
    )
    autocomplete_fields = (
        "course",
        "group",
        "teacher",
        "course_lesson",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )
    date_hierarchy = "date"
    ordering = (
        "-date",
        "lesson_number",
        "id",
    )
    list_select_related = (
        "course",
        "group",
        "teacher",
        "course_lesson",
    )
    inlines = (
        AttendanceInline,
        GradeInline,
    )

    fieldsets = (
        (
            _("Основное"),
            {
                "fields": (
                    "course",
                    "group",
                    "teacher",
                    "course_lesson",
                    "lesson_number",
                )
            },
        ),
        (
            _("Время"),
            {
                "fields": (
                    "date",
                    "started_at",
                    "ended_at",
                )
            },
        ),
        (
            _("Тема занятия"),
            {
                "fields": (
                    "planned_topic",
                    "actual_topic",
                    "homework",
                )
            },
        ),
        (
            _("Статус и комментарий"),
            {
                "fields": (
                    "status",
                    "teacher_comment",
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

    @admin.display(description=_("Тема"))
    def topic(self, obj: JournalLesson) -> str:
        return obj.topic or "—"
