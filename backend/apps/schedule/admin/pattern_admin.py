from __future__ import annotations

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.schedule.models import SchedulePattern, SchedulePatternAudience


class SchedulePatternAudienceInline(admin.TabularInline):
    model = SchedulePatternAudience
    extra = 0
    fields = (
        "audience_type",
        "group",
        "subgroup_name",
        "student",
        "course_enrollment",
        "notes",
    )
    autocomplete_fields = (
        "group",
        "student",
        "course_enrollment",
    )


@admin.register(SchedulePattern)
class SchedulePatternAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title_display",
        "organization",
        "academic_year",
        "education_period",
        "weekday",
        "time_slot",
        "group",
        "subject",
        "teacher",
        "room",
        "lesson_type",
        "source_type",
        "status",
        "is_active",
    )
    list_filter = (
        "is_active",
        "status",
        "source_type",
        "lesson_type",
        "weekday",
        "organization",
        "academic_year",
        "education_period",
        "week_template",
    )
    search_fields = (
        "title",
        "notes",
        "group__name",
        "subject__name",
        "teacher__email",
        "teacher__profile__last_name",
        "teacher__profile__first_name",
        "room__name",
        "room__number",
        "course__title",
        "course_lesson__title",
    )
    ordering = (
        "organization",
        "weekday",
        "time_slot",
        "group",
        "subject",
    )
    list_select_related = (
        "organization",
        "academic_year",
        "education_period",
        "week_template",
        "time_slot",
        "group",
        "subject",
        "teacher",
        "room",
        "group_subject",
        "teacher_group_subject",
        "course",
        "course_lesson",
    )
    autocomplete_fields = (
        "organization",
        "academic_year",
        "education_period",
        "week_template",
        "time_slot",
        "group",
        "subject",
        "teacher",
        "room",
        "group_subject",
        "teacher_group_subject",
        "course",
        "course_lesson",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )
    inlines = (SchedulePatternAudienceInline,)
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "organization",
                    "academic_year",
                    "education_period",
                    "week_template",
                    "status",
                    "is_active",
                    "priority",
                )
            },
        ),
        (
            _("Время"),
            {
                "fields": (
                    "weekday",
                    "time_slot",
                    "starts_at",
                    "ends_at",
                    "starts_on",
                    "ends_on",
                    "repeat_rule",
                )
            },
        ),
        (
            _("Участники"),
            {
                "fields": (
                    "group",
                    "subject",
                    "teacher",
                    "room",
                )
            },
        ),
        (
            _("Связи с учебным процессом"),
            {
                "fields": (
                    "group_subject",
                    "teacher_group_subject",
                    "course",
                    "course_lesson",
                )
            },
        ),
        (
            _("Описание занятия"),
            {
                "fields": (
                    "title",
                    "lesson_type",
                    "source_type",
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

    @admin.display(description=_("Название"))
    def title_display(self, obj: SchedulePattern) -> str:
        if obj.title:
            return obj.title
        if obj.subject_id:
            return str(obj.subject)
        if obj.course_lesson_id:
            return str(obj.course_lesson)
        return _("Занятие")
