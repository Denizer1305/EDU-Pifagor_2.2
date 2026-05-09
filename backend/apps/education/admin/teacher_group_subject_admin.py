from __future__ import annotations

from django.contrib import admin
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.education.models import TeacherGroupSubject


@admin.register(TeacherGroupSubject)
class TeacherGroupSubjectAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "teacher_full_name",
        "teacher_email",
        "group_subject",
        "role",
        "is_primary",
        "is_active",
        "planned_hours",
        "starts_at",
        "ends_at",
        "is_current_display",
    )
    list_display_links = (
        "id",
        "teacher_full_name",
    )
    list_filter = (
        "role",
        "is_primary",
        "is_active",
        "group_subject__academic_year",
        "group_subject__period",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "teacher__email",
        "teacher__profile__last_name",
        "teacher__profile__first_name",
        "teacher__profile__patronymic",
        "group_subject__group__name",
        "group_subject__group__code",
        "group_subject__subject__name",
        "group_subject__subject__short_name",
        "notes",
    )
    autocomplete_fields = (
        "teacher",
        "group_subject",
    )
    ordering = (
        "group_subject",
        "teacher",
    )
    readonly_fields = (
        "is_current_display",
        "created_at",
        "updated_at",
    )
    list_select_related = (
        "teacher",
        "teacher__profile",
        "group_subject",
        "group_subject__group",
        "group_subject__subject",
        "group_subject__academic_year",
        "group_subject__period",
    )
    date_hierarchy = "starts_at"

    fieldsets = (
        (
            _("Основное"),
            {
                "fields": (
                    "teacher",
                    "group_subject",
                    "role",
                )
            },
        ),
        (
            _("Статус"),
            {
                "fields": (
                    "is_primary",
                    "is_active",
                    "planned_hours",
                    "is_current_display",
                )
            },
        ),
        (
            _("Даты"),
            {
                "fields": (
                    "starts_at",
                    "ends_at",
                )
            },
        ),
        (_("Дополнительно"), {"fields": ("notes",)}),
        (
            _("Служебное"),
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )

    @admin.display(description=_("Преподаватель"))
    def teacher_full_name(self, obj: TeacherGroupSubject) -> str:
        return getattr(obj.teacher, "full_name", obj.teacher.email)

    @admin.display(description=_("Email"))
    def teacher_email(self, obj: TeacherGroupSubject) -> str:
        return obj.teacher.email

    @admin.display(description=_("Текущее"), boolean=True)
    def is_current_display(self, obj: TeacherGroupSubject) -> bool:
        today = timezone.localdate()

        has_started = not obj.starts_at or obj.starts_at <= today
        has_not_ended = not obj.ends_at or obj.ends_at >= today

        return obj.is_active and has_started and has_not_ended
