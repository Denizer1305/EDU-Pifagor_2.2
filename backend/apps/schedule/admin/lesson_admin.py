from __future__ import annotations

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.schedule.models import ScheduledLesson, ScheduledLessonAudience


class ScheduledLessonAudienceInline(admin.TabularInline):
    model = ScheduledLessonAudience
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


@admin.register(ScheduledLesson)
class ScheduledLessonAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "date",
        "time_slot",
        "title_display",
        "organization",
        "group",
        "subject",
        "teacher",
        "room",
        "lesson_type",
        "source_type",
        "status",
        "is_public",
        "is_locked",
    )
    list_filter = (
        "status",
        "source_type",
        "lesson_type",
        "is_public",
        "is_locked",
        "generated_from_pattern",
        "organization",
        "academic_year",
        "education_period",
        "date",
    )
    search_fields = (
        "title",
        "planned_topic",
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
    date_hierarchy = "date"
    ordering = (
        "-date",
        "time_slot",
        "group",
        "subject",
    )
    list_select_related = (
        "organization",
        "academic_year",
        "education_period",
        "pattern",
        "time_slot",
        "group",
        "subject",
        "teacher",
        "room",
        "group_subject",
        "teacher_group_subject",
        "course",
        "course_lesson",
        "journal_lesson",
        "generation_batch",
        "created_by",
        "updated_by",
    )
    autocomplete_fields = (
        "organization",
        "academic_year",
        "education_period",
        "pattern",
        "time_slot",
        "group",
        "subject",
        "teacher",
        "room",
        "group_subject",
        "teacher_group_subject",
        "course",
        "course_lesson",
        "journal_lesson",
        "generation_batch",
        "created_by",
        "updated_by",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )
    inlines = (ScheduledLessonAudienceInline,)
    actions = (
        "publish_lessons",
        "unpublish_lessons",
        "lock_lessons",
        "unlock_lessons",
    )
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "organization",
                    "academic_year",
                    "education_period",
                    "pattern",
                    "status",
                    "is_public",
                    "is_locked",
                    "generated_from_pattern",
                    "generation_batch",
                )
            },
        ),
        (
            _("Дата и время"),
            {
                "fields": (
                    "date",
                    "weekday",
                    "time_slot",
                    "starts_at",
                    "ends_at",
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
                    "journal_lesson",
                )
            },
        ),
        (
            _("Описание занятия"),
            {
                "fields": (
                    "title",
                    "planned_topic",
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
                    "created_by",
                    "updated_by",
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )

    @admin.display(description=_("Название"))
    def title_display(self, obj: ScheduledLesson) -> str:
        if obj.title:
            return obj.title
        if obj.subject_id:
            return str(obj.subject)
        if obj.course_lesson_id:
            return str(obj.course_lesson)
        return _("Занятие")

    @admin.action(description=_("Опубликовать выбранные занятия"))
    def publish_lessons(self, request, queryset):
        queryset.update(is_public=True)

    @admin.action(description=_("Снять выбранные занятия с публикации"))
    def unpublish_lessons(self, request, queryset):
        queryset.update(is_public=False)

    @admin.action(description=_("Заблокировать выбранные занятия"))
    def lock_lessons(self, request, queryset):
        queryset.update(is_locked=True)

    @admin.action(description=_("Разблокировать выбранные занятия"))
    def unlock_lessons(self, request, queryset):
        queryset.update(is_locked=False)
