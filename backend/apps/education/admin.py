from __future__ import annotations

from django.contrib import admin
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.education.models import (
    AcademicYear,
    Curriculum,
    CurriculumItem,
    EducationPeriod,
    GroupSubject,
    StudentGroupEnrollment,
    TeacherGroupSubject,
)


@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = (
        "id", "name",
        "start_date", "end_date",
        "is_current", "is_active",
        "created_at",
    )
    list_display_links = (
        "id", "name",
    )
    list_filter = (
        "is_current", "is_active",
        "created_at", "updated_at",
    )
    search_fields = (
        "name", "description",
    )
    ordering = (
        "-start_date",
    )
    readonly_fields = (
        "created_at", "updated_at",
    )
    date_hierarchy = "start_date"

    fieldsets = (
        (_("Основное"), {
            "fields": (
                "name", "start_date",
                "end_date", "description",
            )
        }),
        (_("Статус"), {
            "fields": (
                "is_current", "is_active",
            )
        }),
        (_("Служебное"), {
            "fields": (
                "created_at", "updated_at",
            )
        }),
    )


@admin.register(EducationPeriod)
class EducationPeriodAdmin(admin.ModelAdmin):
    list_display = (
        "id", "name",
        "code", "academic_year",
        "period_type", "sequence",
        "start_date", "end_date",
        "is_current", "is_active",
    )
    list_display_links = (
        "id", "name",
    )
    list_filter = (
        "academic_year", "period_type",
        "is_current", "is_active",
        "created_at", "updated_at",
    )
    search_fields = (
        "name", "code",
        "academic_year__name",
        "description",
    )
    autocomplete_fields = (
        "academic_year",
    )
    ordering = (
        "academic_year", "sequence",
    )
    readonly_fields = (
        "created_at", "updated_at",
    )
    list_select_related = (
        "academic_year",
    )
    date_hierarchy = "start_date"

    fieldsets = (
        (_("Основное"), {
            "fields": (
                "academic_year", "name",
                "code", "period_type",
                "sequence",
            )
        }),
        (_("Даты"), {
            "fields": (
                "start_date", "end_date",
            )
        }),
        (_("Описание и статус"), {
            "fields": (
                "description", "is_current",
                "is_active",
            )
        }),
        (_("Служебное"), {
            "fields": (
                "created_at", "updated_at",
            )
        }),
    )


@admin.register(StudentGroupEnrollment)
class StudentGroupEnrollmentAdmin(admin.ModelAdmin):
    list_display = (
        "id", "student_full_name",
        "student_email", "group",
        "academic_year", "status",
        "is_primary", "journal_number",
        "enrollment_date", "completion_date",
        "is_current_display",
    )
    list_display_links = (
        "id", "student_full_name",
    )
    list_filter = (
        "academic_year", "status",
        "is_primary", "group",
        "created_at", "updated_at",
    )
    search_fields = (
        "student__email",
        "student__profile__last_name",
        "student__profile__first_name",
        "student__profile__patronymic",
        "group__name", "group__code",
        "academic_year__name",
        "notes",
    )
    autocomplete_fields = (
        "student", "group",
        "academic_year",
    )
    ordering = (
        "-academic_year__start_date", "group",
        "student",
    )
    readonly_fields = (
        "is_current_display",
        "created_at", "updated_at",
    )
    list_select_related = (
        "student", "student__profile",
        "group", "academic_year",
    )
    date_hierarchy = "enrollment_date"

    fieldsets = (
        (_("Основное"), {
            "fields": (
                "student", "group",
                "academic_year",
            )
        }),
        (_("Статус зачисления"), {
            "fields": (
                "status", "is_primary",
                "journal_number", "is_current_display",
            )
        }),
        (_("Даты"), {
            "fields": (
                "enrollment_date", "completion_date",
            )
        }),
        (_("Дополнительно"), {
            "fields": (
                "notes",
            )
        }),
        (_("Служебное"), {
            "fields": (
                "created_at", "updated_at",
            )
        }),
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


@admin.register(GroupSubject)
class GroupSubjectAdmin(admin.ModelAdmin):
    list_display = (
        "id", "group",
        "subject", "academic_year",
        "period", "planned_hours",
        "contact_hours", "independent_hours",
        "assessment_type", "is_required",
        "is_active",
    )
    list_display_links = (
        "id", "group",
    )
    list_filter = (
        "academic_year", "period",
        "assessment_type", "is_required",
        "is_active", "created_at",
        "updated_at",
    )
    search_fields = (
        "group__name", "group__code",
        "subject__name", "subject__short_name",
        "academic_year__name",
        "period__name",
        "notes",
    )
    autocomplete_fields = (
        "group", "subject",
        "academic_year", "period",
    )
    ordering = (
        "group", "period__sequence",
        "subject",
    )
    readonly_fields = (
        "hours_balance_display",
        "created_at", "updated_at",
    )
    list_select_related = (
        "group", "subject",
        "academic_year", "period",
    )

    fieldsets = (
        (_("Основное"), {
            "fields": (
                "group", "subject",
                "academic_year", "period",
            )
        }),
        (_("Нагрузка"), {
            "fields": (
                "planned_hours", "contact_hours",
                "independent_hours", "hours_balance_display",
            )
        }),
        (_("Аттестация и статус"), {
            "fields": (
                "assessment_type", "is_required",
                "is_active",
            )
        }),
        (_("Дополнительно"), {
            "fields": (
                "notes",
            )
        }),
        (_("Служебное"), {
            "fields": (
                "created_at", "updated_at",
            )
        }),
    )

    @admin.display(description=_("Остаток часов"))
    def hours_balance_display(self, obj: GroupSubject) -> int:
        return obj.planned_hours - (obj.contact_hours + obj.independent_hours)


@admin.register(TeacherGroupSubject)
class TeacherGroupSubjectAdmin(admin.ModelAdmin):
    list_display = (
        "id", "teacher_full_name",
        "teacher_email", "group_subject",
        "role", "is_primary",
        "is_active", "planned_hours",
        "starts_at", "ends_at",
        "is_current_display",
    )
    list_display_links = (
        "id", "teacher_full_name",
    )
    list_filter = (
        "role", "is_primary",
        "is_active",
        "group_subject__academic_year",
        "group_subject__period",
        "created_at", "updated_at",
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
        "teacher", "group_subject",
    )
    ordering = (
        "group_subject", "teacher",
    )
    readonly_fields = (
        "is_current_display",
        "created_at", "updated_at",
    )
    list_select_related = (
        "teacher", "teacher__profile",
        "group_subject",
        "group_subject__group",
        "group_subject__subject",
        "group_subject__academic_year",
        "group_subject__period",
    )
    date_hierarchy = "starts_at"

    fieldsets = (
        (_("Основное"), {
            "fields": (
                "teacher", "group_subject",
                "role",
            )
        }),
        (_("Статус"), {
            "fields": (
                "is_primary", "is_active",
                "planned_hours", "is_current_display",
            )
        }),
        (_("Даты"), {
            "fields": (
                "starts_at", "ends_at",
            )
        }),
        (_("Дополнительно"), {
            "fields": (
                "notes",
            )
        }),
        (_("Служебное"), {
            "fields": (
                "created_at", "updated_at",
            )
        }),
    )

    @admin.display(description=_("Преподаватель"))
    def teacher_full_name(self, obj: TeacherGroupSubject) -> str:
        return getattr(obj.teacher, "full_name", obj.teacher.email)

    @admin.display(description=_("Email"))
    def teacher_email(self, obj: TeacherGroupSubject) -> str:
        return obj.teacher.email

    @admin.display(description=_("Текущее"), boolean=True)
    def is_current_display(self, obj: TeacherGroupSubject) -> bool:
        if not obj.is_active:
            return False

        today = timezone.localdate()

        if obj.starts_at and obj.starts_at > today:
            return False

        if obj.ends_at and obj.ends_at < today:
            return False

        return True


class CurriculumItemInline(admin.TabularInline):
    model = CurriculumItem
    extra = 0
    autocomplete_fields = (
        "period", "subject",
    )
    fields = (
        "period", "subject",
        "sequence", "planned_hours",
        "contact_hours", "independent_hours",
        "assessment_type", "is_required",
        "is_active",
    )
    ordering = (
        "period__sequence", "sequence",
    )
    show_change_link = True


@admin.register(Curriculum)
class CurriculumAdmin(admin.ModelAdmin):
    list_display = (
        "id", "name",
        "code", "organization",
        "department", "academic_year",
        "total_hours", "is_active",
        "created_at",
    )
    list_display_links = (
        "id", "name",
    )
    list_filter = (
        "organization", "department",
        "academic_year", "is_active",
        "created_at", "updated_at",
    )
    search_fields = (
        "name", "code",
        "organization__name",
        "organization__short_name",
        "department__name",
        "department__short_name",
        "academic_year__name",
        "description",
    )
    autocomplete_fields = (
        "organization", "department",
        "academic_year",
    )
    ordering = (
        "organization", "name",
    )
    readonly_fields = (
        "created_at", "updated_at",
    )
    list_select_related = (
        "organization", "department",
        "academic_year",
    )
    inlines = [CurriculumItemInline]

    fieldsets = (
        (_("Основное"), {
            "fields": (
                "organization", "department",
                "academic_year", "code",
                "name",
            )
        }),
        (_("Описание и нагрузка"), {
            "fields": (
                "description", "total_hours",
            )
        }),
        (_("Статус"), {
            "fields": (
                "is_active",
            )
        }),
        (_("Служебное"), {
            "fields": (
                "created_at", "updated_at",
            )
        }),
    )


@admin.register(CurriculumItem)
class CurriculumItemAdmin(admin.ModelAdmin):
    list_display = (
        "id", "curriculum",
        "period", "subject",
        "sequence", "planned_hours",
        "contact_hours", "independent_hours",
        "assessment_type", "is_required",
        "is_active",
    )
    list_display_links = (
        "id", "curriculum",
    )
    list_filter = (
        "curriculum__academic_year",
        "period", "assessment_type",
        "is_required", "is_active",
        "created_at", "updated_at",
    )
    search_fields = (
        "curriculum__name",
        "curriculum__code",
        "subject__name",
        "subject__short_name",
        "period__name",
        "notes",
    )
    autocomplete_fields = (
        "curriculum", "period",
        "subject",
    )
    ordering = (
        "curriculum", "period__sequence",
        "sequence",
    )
    readonly_fields = (
        "hours_balance_display",
        "created_at", "updated_at",
    )
    list_select_related = (
        "curriculum", "period",
        "subject",
        "curriculum__academic_year",
    )

    fieldsets = (
        (_("Основное"), {
            "fields": (
                "curriculum", "period",
                "subject", "sequence",
            )
        }),
        (_("Нагрузка"), {
            "fields": (
                "planned_hours", "contact_hours",
                "independent_hours", "hours_balance_display",
            )
        }),
        (_("Аттестация и статус"), {
            "fields": (
                "assessment_type", "is_required",
                "is_active",
            )
        }),
        (_("Дополнительно"), {
            "fields": (
                "notes",
            )
        }),
        (_("Служебное"), {
            "fields": (
                "created_at", "updated_at",
            )
        }),
    )

    @admin.display(description=_("Остаток часов"))
    def hours_balance_display(self, obj: CurriculumItem) -> int:
        return obj.planned_hours - (obj.contact_hours + obj.independent_hours)
