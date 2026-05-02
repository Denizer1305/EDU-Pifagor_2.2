from __future__ import annotations

from django.contrib import admin
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.education.models import StudentGroupEnrollment


@admin.register(StudentGroupEnrollment)
class StudentGroupEnrollmentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "student_full_name",
        "student_email",
        "group",
        "academic_year",
        "status",
        "is_primary",
        "journal_number",
        "enrollment_date",
        "completion_date",
        "is_current_display",
    )
    list_display_links = (
        "id",
        "student_full_name",
    )
    list_filter = (
        "academic_year",
        "status",
        "is_primary",
        "group",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "student__email",
        "student__profile__last_name",
        "student__profile__first_name",
        "student__profile__patronymic",
        "group__name",
        "group__code",
        "academic_year__name",
        "notes",
    )
    autocomplete_fields = (
        "student",
        "group",
        "academic_year",
    )
    ordering = (
        "-academic_year__start_date",
        "group",
        "student",
    )
    readonly_fields = (
        "is_current_display",
        "created_at",
        "updated_at",
    )
    list_select_related = (
        "student",
        "student__profile",
        "group",
        "academic_year",
    )
    date_hierarchy = "enrollment_date"

    fieldsets = (
        (
            _("Основное"),
            {
                "fields": (
                    "student",
                    "group",
                    "academic_year",
                )
            },
        ),
        (
            _("Статус зачисления"),
            {
                "fields": (
                    "status",
                    "is_primary",
                    "journal_number",
                    "is_current_display",
                )
            },
        ),
        (
            _("Даты"),
            {
                "fields": (
                    "enrollment_date",
                    "completion_date",
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

    @admin.display(description=_("Студент"))
    def student_full_name(self, obj: StudentGroupEnrollment) -> str:
        return getattr(obj.student, "full_name", obj.student.email)

    @admin.display(description=_("Email"))
    def student_email(self, obj: StudentGroupEnrollment) -> str:
        return obj.student.email

    @admin.display(description=_("Текущее"), boolean=True)
    def is_current_display(self, obj: StudentGroupEnrollment) -> bool:
        today = timezone.localdate()

        if obj.status != StudentGroupEnrollment.StatusChoices.ACTIVE:
            return False

        if obj.enrollment_date and obj.enrollment_date > today:
            return False

        if obj.completion_date and obj.completion_date < today:
            return False

        return True
