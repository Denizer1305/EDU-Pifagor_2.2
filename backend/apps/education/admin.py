from django.contrib import admin
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
    list_filter = (
        "is_current", "is_active",
        "created_at",
    )
    search_fields = (
        "name",
    )
    ordering = ("-start_date",)
    readonly_fields = (
        "created_at", "updated_at",
    )

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
    list_filter = (
        "academic_year", "period_type",
        "is_current", "is_active",
    )
    search_fields = (
        "name", "code",
        "academic_year__name",
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
        "id", "student",
        "group", "academic_year",
        "status", "is_primary",
        "journal_number", "enrollment_date",
        "completion_date",
    )
    list_filter = (
        "academic_year", "status",
        "is_primary", "group",
    )
    search_fields = (
        "student__email",
        "student__profile__last_name",
        "student__profile__first_name",
        "group__name", "group__code",
        "academic_year__name",
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
        "created_at", "updated_at",
    )

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
                "journal_number",
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


@admin.register(GroupSubject)
class GroupSubjectAdmin(admin.ModelAdmin):
    list_display = (
        "id", "group",
        "subject", "academic_year",
        "period", "planned_hours",
        "assessment_type", "is_required",
        "is_active",
    )
    list_filter = (
        "academic_year", "period",
        "assessment_type", "is_required",
        "is_active",
    )
    search_fields = (
        "group__name", "group__code",
        "subject__name", "subject__short_name",
        "academic_year__name",
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
        "created_at", "updated_at",
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
                "independent_hours",
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


@admin.register(TeacherGroupSubject)
class TeacherGroupSubjectAdmin(admin.ModelAdmin):
    list_display = (
        "id", "teacher",
        "group_subject", "role",
        "is_primary", "is_active",
        "planned_hours", "starts_at",
        "ends_at",
    )
    list_filter = (
        "role", "is_primary",
        "is_active", "group_subject__academic_year",
    )
    search_fields = (
        "teacher__email",
        "teacher__profile__last_name",
        "teacher__profile__first_name",
        "group_subject__group__name",
        "group_subject__subject__name",
    )
    autocomplete_fields = (
        "teacher", "group_subject",
    )
    ordering = (
        "group_subject", "teacher",
    )
    readonly_fields = (
        "created_at", "updated_at",
    )

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
                "planned_hours",
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


@admin.register(Curriculum)
class CurriculumAdmin(admin.ModelAdmin):
    list_display = (
        "id", "name",
        "code", "organization",
        "department", "academic_year",
        "total_hours", "is_active",
    )
    list_filter = (
        "organization", "department",
        "academic_year", "is_active",
    )
    search_fields = (
        "name", "code",
        "organization__name",
        "department__name",
        "academic_year__name",
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
        "assessment_type", "is_required",
        "is_active",
    )
    list_filter = (
        "curriculum__academic_year",
        "period", "assessment_type",
        "is_required", "is_active",
    )
    search_fields = (
        "curriculum__name",
        "subject__name",
        "subject__short_name",
        "period__name",
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
        "created_at", "updated_at",
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
                "independent_hours",
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
