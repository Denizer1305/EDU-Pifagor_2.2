from __future__ import annotations

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.journal.models import (
    AttendanceRecord,
    JournalGrade,
    JournalLesson,
    JournalSummary,
    TopicProgress,
)


class AttendanceInline(admin.TabularInline):
    """Посещаемость студентов прямо в карточке занятия."""

    model = AttendanceRecord
    extra = 0
    fields = ("student", "status", "comment")
    autocomplete_fields = ("student",)


class GradeInline(admin.TabularInline):
    """Оценки студентов прямо в карточке занятия."""

    model = JournalGrade
    extra = 0
    fields = (
        "student",
        "grade_type",
        "scale",
        "score_five",
        "score_points",
        "is_passed",
        "weight",
        "comment",
    )
    autocomplete_fields = ("student",)


@admin.register(JournalLesson)
class JournalLessonAdmin(admin.ModelAdmin):
    """Администрирование занятий журнала."""

    list_display = (
        "id",
        "date",
        "course",
        "group",
        "teacher",
        "status",
        "topic",
        "lesson_number",
    )
    list_filter = ("status", "date", "course", "group")
    search_fields = (
        "planned_topic",
        "actual_topic",
        "teacher__user__last_name",
        "group__name",
        "course__title",
    )
    autocomplete_fields = ("course", "group", "teacher", "course_lesson")
    date_hierarchy = "date"
    ordering = ("-date",)
    inlines = [AttendanceInline, GradeInline]

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
            {"fields": ("date", "started_at", "ended_at")},
        ),
        (
            _("Тема"),
            {"fields": ("planned_topic", "actual_topic", "homework")},
        ),
        (
            _("Статус и комментарий"),
            {"fields": ("status", "teacher_comment")},
        ),
    )

    @admin.display(description=_("Тема"))
    def topic(self, obj: JournalLesson) -> str:
        return obj.topic or "—"


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    """Администрирование записей посещаемости."""

    list_display = ("id", "lesson", "student", "status", "comment")
    list_filter = ("status", "lesson__date", "lesson__course")
    search_fields = (
        "student__user__last_name",
        "lesson__planned_topic",
        "lesson__actual_topic",
    )
    autocomplete_fields = ("lesson", "student")
    ordering = ("-lesson__date",)


@admin.register(JournalGrade)
class JournalGradeAdmin(admin.ModelAdmin):
    """Администрирование оценок в журнале."""

    list_display = (
        "id",
        "lesson",
        "student",
        "grade_type",
        "scale",
        "display_value",
        "weight",
        "is_auto",
        "graded_by",
    )
    list_filter = ("grade_type", "scale", "is_auto", "lesson__course")
    search_fields = (
        "student__user__last_name",
        "lesson__planned_topic",
    )
    autocomplete_fields = (
        "lesson",
        "student",
        "graded_by",
        "submission",
        "grade_record",
    )
    ordering = ("-lesson__date",)

    @admin.display(description=_("Значение"))
    def display_value(self, obj: JournalGrade) -> str:
        return obj.display_value


@admin.register(TopicProgress)
class TopicProgressAdmin(admin.ModelAdmin):
    """Администрирование прогресса прохождения тем."""

    list_display = (
        "id",
        "course",
        "group",
        "lesson",
        "planned_date",
        "actual_date",
        "status",
        "days_behind",
    )
    list_filter = ("status", "course", "group")
    search_fields = (
        "lesson__title",
        "course__title",
        "group__name",
    )
    autocomplete_fields = ("course", "group", "lesson", "journal_lesson")
    ordering = ("planned_date",)

    @admin.display(description=_("Отстаёт?"), boolean=True)
    def is_behind(self, obj: TopicProgress) -> bool:
        return obj.is_behind


@admin.register(JournalSummary)
class JournalSummaryAdmin(admin.ModelAdmin):
    """Администрирование кэша сводок журнала. Только для просмотра."""

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
    list_filter = ("course", "group")
    search_fields = (
        "student__user__last_name",
        "group__name",
        "course__title",
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

    def has_add_permission(self, request) -> bool:  # noqa: ANN001
        return False

    def has_change_permission(self, request, obj=None) -> bool:  # noqa: ANN001
        return False
