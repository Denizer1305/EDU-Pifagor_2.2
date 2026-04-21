from __future__ import annotations

from django.contrib import admin, messages
from django.utils.translation import gettext_lazy as _

from apps.organizations.models import (
    Department,
    Group,
    GroupCurator,
    Organization,
    OrganizationType,
    Subject,
    SubjectCategory,
    TeacherOrganization,
    TeacherSubject,
)


@admin.register(OrganizationType)
class OrganizationTypeAdmin(admin.ModelAdmin):
    list_display = (
        "id", "name",
        "code", "is_active",
        "created_at", "updated_at",
    )
    list_display_links = (
        "id", "name",
    )
    list_filter = (
        "is_active", "created_at",
        "updated_at",
    )
    search_fields = (
        "name", "code",
        "description",
    )
    ordering = (
        "name",
    )
    readonly_fields = (
        "created_at", "updated_at",
    )

    fieldsets = (
        (_("Основное"), {
            "fields": (
                "name", "code",
                "description", "is_active",
            )
        }),
        (_("Служебное"), {
            "fields": (
                "created_at", "updated_at",
            )
        }),
    )


@admin.action(description=_("Отключить код регистрации преподавателя"))
def disable_teacher_registration_code(modeladmin, request, queryset):
    updated_count = 0

    for obj in queryset:
        if hasattr(obj, "disable_teacher_registration_code"):
            obj.disable_teacher_registration_code()
            obj.save(update_fields=(
                "teacher_registration_code_is_active",
                "updated_at",
            ))
            updated_count += 1

    modeladmin.message_user(
        request,
        _("Отключено кодов регистрации преподавателя: %(count)s") % {"count": updated_count},
        level=messages.SUCCESS,
    )


@admin.action(description=_("Очистить код регистрации преподавателя"))
def clear_teacher_registration_code(modeladmin, request, queryset):
    updated_count = 0

    for obj in queryset:
        if hasattr(obj, "clear_teacher_registration_code"):
            obj.clear_teacher_registration_code()
            obj.save(update_fields=(
                "teacher_registration_code_hash",
                "teacher_registration_code_is_active",
                "teacher_registration_code_expires_at",
                "updated_at",
            ))
            updated_count += 1

    modeladmin.message_user(
        request,
        _("Очищено кодов регистрации преподавателя: %(count)s") % {"count": updated_count},
        level=messages.SUCCESS,
    )


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = (
        "id", "name",
        "short_name", "type",
        "city", "email",
        "teacher_code_active_display",
        "teacher_registration_code_expires_at",
        "is_active", "created_at",
    )
    list_display_links = (
        "id", "name",
    )
    list_filter = (
        "type", "city",
        "is_active",
        "teacher_registration_code_is_active",
        "created_at", "updated_at",
    )
    search_fields = (
        "name", "short_name",
        "city", "email",
        "phone", "address",
        "website",
    )
    autocomplete_fields = (
        "type",
    )
    ordering = (
        "name",
    )
    readonly_fields = (
        "teacher_registration_code_hash",
        "has_active_teacher_registration_code_display",
        "created_at", "updated_at",
    )
    actions = (
        disable_teacher_registration_code,
        clear_teacher_registration_code,
    )

    fieldsets = (
        (_("Основное"), {
            "fields": (
                "name", "short_name",
                "type", "description",
            )
        }),
        (_("Контактные данные"), {
            "fields": (
                "city",
                "address",
                "phone",
                "email",
                "website",
            )
        }),
        (_("Логотип"), {
            "fields": (
                "logo",
            )
        }),
        (_("Код регистрации преподавателя"), {
            "fields": (
                "teacher_registration_code_hash",
                "teacher_registration_code_is_active",
                "teacher_registration_code_expires_at",
                "has_active_teacher_registration_code_display",
            )
        }),
        (_("Статус"), {
            "fields": (
                "is_active",
            )
        }),
        (_("Служебное"), {
            "fields": (
                "created_at",
                "updated_at",
            )
        }),
    )

    @admin.display(description=_("Код преподавателя активен"), boolean=True)
    def teacher_code_active_display(self, obj: Organization) -> bool:
        return obj.has_active_teacher_registration_code

    @admin.display(description=_("Есть активный код"), boolean=True)
    def has_active_teacher_registration_code_display(self, obj: Organization) -> bool:
        return obj.has_active_teacher_registration_code


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = (
        "id", "name",
        "short_name", "organization",
        "is_active", "created_at",
        "updated_at",
    )
    list_display_links = (
        "id", "name",
    )
    list_filter = (
        "organization", "is_active",
        "created_at", "updated_at",
    )
    search_fields = (
        "name", "short_name",
        "organization__name", "organization__short_name",
        "description",
    )
    autocomplete_fields = (
        "organization",
    )
    ordering = (
        "organization", "name",
    )
    readonly_fields = (
        "created_at", "updated_at",
    )

    fieldsets = (
        (_("Основное"), {
            "fields": (
                "organization",
                "name",
                "short_name",
                "description",
            )
        }),
        (_("Статус"), {
            "fields": (
                "is_active",
            )
        }),
        (_("Служебное"), {
            "fields": (
                "created_at",
                "updated_at",
            )
        }),
    )


@admin.action(description=_("Отключить код присоединения к группе"))
def disable_group_join_code(modeladmin, request, queryset):
    updated_count = 0

    for obj in queryset:
        if hasattr(obj, "disable_join_code"):
            obj.disable_join_code()
            obj.save(update_fields=(
                "join_code_is_active",
                "updated_at",
            ))
            updated_count += 1

    modeladmin.message_user(
        request,
        _("Отключено кодов группы: %(count)s") % {"count": updated_count},
        level=messages.SUCCESS,
    )


@admin.action(description=_("Очистить код присоединения к группе"))
def clear_group_join_code(modeladmin, request, queryset):
    updated_count = 0

    for obj in queryset:
        if hasattr(obj, "clear_join_code"):
            obj.clear_join_code()
            obj.save(update_fields=(
                "join_code_hash",
                "join_code_is_active",
                "join_code_expires_at",
                "updated_at",
            ))
            updated_count += 1

    modeladmin.message_user(
        request,
        _("Очищено кодов группы: %(count)s") % {"count": updated_count},
        level=messages.SUCCESS,
    )


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = (
        "id", "name",
        "code", "organization",
        "department", "study_form",
        "course_number", "academic_year",
        "group_join_code_active_display",
        "status", "is_active",
        "created_at",
    )
    list_display_links = (
        "id", "name",
    )
    list_filter = (
        "organization", "department",
        "study_form", "status",
        "admission_year", "graduation_year",
        "academic_year", "is_active",
        "join_code_is_active",
        "created_at", "updated_at",
    )
    search_fields = (
        "name", "code",
        "organization__name", "organization__short_name",
        "department__name",
        "description",
    )
    autocomplete_fields = (
        "organization", "department",
    )
    ordering = (
        "organization", "name",
    )
    readonly_fields = (
        "join_code_hash",
        "has_active_join_code_display",
        "created_at", "updated_at",
    )
    actions = (
        disable_group_join_code,
        clear_group_join_code,
    )

    fieldsets = (
        (_("Основное"), {
            "fields": (
                "organization",
                "department",
                "name",
                "code",
                "description",
            )
        }),
        (_("Учебные параметры"), {
            "fields": (
                "study_form",
                "course_number",
                "admission_year",
                "graduation_year",
                "academic_year",
                "status",
            )
        }),
        (_("Код присоединения к группе"), {
            "fields": (
                "join_code_hash",
                "join_code_is_active",
                "join_code_expires_at",
                "has_active_join_code_display",
            )
        }),
        (_("Статус"), {
            "fields": (
                "is_active",
            )
        }),
        (_("Служебное"), {
            "fields": (
                "created_at",
                "updated_at",
            )
        }),
    )

    @admin.display(description=_("Код группы активен"), boolean=True)
    def group_join_code_active_display(self, obj: Group) -> bool:
        return obj.has_active_join_code

    @admin.display(description=_("Есть активный код"), boolean=True)
    def has_active_join_code_display(self, obj: Group) -> bool:
        return obj.has_active_join_code


@admin.register(GroupCurator)
class GroupCuratorAdmin(admin.ModelAdmin):
    list_display = (
        "id", "group",
        "teacher", "is_primary",
        "is_active", "starts_at",
        "ends_at", "is_current_display",
        "created_at",
    )
    list_display_links = (
        "id", "group",
    )
    list_filter = (
        "is_primary", "is_active",
        "starts_at", "ends_at",
        "created_at", "updated_at",
    )
    search_fields = (
        "group__name", "group__code",
        "teacher__email", "teacher__profile__last_name",
        "teacher__profile__first_name",
        "notes",
    )
    autocomplete_fields = (
        "group", "teacher",
    )
    ordering = (
        "-is_primary", "-is_active",
        "-starts_at", "-created_at",
    )
    readonly_fields = (
        "is_current_display",
        "created_at", "updated_at",
    )

    fieldsets = (
        (_("Основное"), {
            "fields": (
                "group",
                "teacher",
                "is_primary",
                "is_active",
            )
        }),
        (_("Период действия"), {
            "fields": (
                "starts_at",
                "ends_at",
                "is_current_display",
            )
        }),
        (_("Примечание"), {
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

    @admin.display(description=_("Актуально сейчас"), boolean=True)
    def is_current_display(self, obj: GroupCurator) -> bool:
        return obj.is_current


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = (
        "id", "name",
        "short_name", "category",
        "is_active", "created_at",
        "updated_at",
    )
    list_display_links = (
        "id", "name",
    )
    list_filter = (
        "category", "is_active",
        "created_at", "updated_at",
    )
    search_fields = (
        "name", "short_name",
        "category__name", "category__code",
        "description",
    )
    autocomplete_fields = (
        "category",
    )
    ordering = (
        "name",
    )
    readonly_fields = (
        "created_at", "updated_at",
    )

    fieldsets = (
        (_("Основное"), {
            "fields": (
                "name", "short_name",
                "category", "description",
            )
        }),
        (_("Статус"), {
            "fields": (
                "is_active",
            )
        }),
        (_("Служебное"), {
            "fields": (
                "created_at",
                "updated_at",
            )
        }),
    )


@admin.register(SubjectCategory)
class SubjectCategoryAdmin(admin.ModelAdmin):
    list_display = (
        "id", "name",
        "code", "is_active",
        "created_at", "updated_at",
    )
    list_display_links = (
        "id", "name",
    )
    list_filter = (
        "is_active", "created_at",
        "updated_at",
    )
    search_fields = (
        "name", "code",
        "description",
    )
    ordering = (
        "name",
    )
    readonly_fields = (
        "created_at", "updated_at",
    )

    fieldsets = (
        (_("Основное"), {
            "fields": (
                "name", "code",
                "description", "is_active",
            )
        }),
        (_("Служебное"), {
            "fields": (
                "created_at", "updated_at",
            )
        }),
    )


@admin.register(TeacherOrganization)
class TeacherOrganizationAdmin(admin.ModelAdmin):
    list_display = (
        "id", "teacher",
        "organization", "position",
        "employment_type", "is_primary",
        "is_active", "starts_at",
        "ends_at", "is_current_display",
        "created_at",
    )
    list_display_links = (
        "id", "teacher",
    )
    list_filter = (
        "employment_type", "is_primary",
        "is_active", "starts_at",
        "ends_at", "created_at",
        "updated_at",
    )
    search_fields = (
        "teacher__email", "teacher__profile__last_name",
        "teacher__profile__first_name", "organization__name",
        "organization__short_name", "position",
        "notes",
    )
    autocomplete_fields = (
        "teacher", "organization",
    )
    ordering = (
        "teacher", "organization",
    )
    readonly_fields = (
        "is_current_display",
        "created_at", "updated_at",
    )

    fieldsets = (
        (_("Основное"), {
            "fields": (
                "teacher",
                "organization",
                "position",
                "employment_type",
            )
        }),
        (_("Статус связи"), {
            "fields": (
                "is_primary",
                "is_active",
                "starts_at",
                "ends_at",
                "is_current_display",
            )
        }),
        (_("Примечание"), {
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

    @admin.display(description=_("Актуально сейчас"), boolean=True)
    def is_current_display(self, obj: TeacherOrganization) -> bool:
        return obj.is_current


@admin.register(TeacherSubject)
class TeacherSubjectAdmin(admin.ModelAdmin):
    list_display = (
        "id", "teacher",
        "subject", "is_primary",
        "is_active", "created_at",
        "updated_at",
    )
    list_display_links = (
        "id", "teacher",
    )
    list_filter = (
        "is_primary", "is_active",
        "subject__category", "created_at",
        "updated_at",
    )
    search_fields = (
        "teacher__email", "teacher__profile__last_name",
        "teacher__profile__first_name", "subject__name",
        "subject__short_name", "subject__category__name",
    )
    autocomplete_fields = (
        "teacher", "subject",
    )
    ordering = (
        "teacher", "subject",
    )
    readonly_fields = (
        "created_at", "updated_at",
    )

    fieldsets = (
        (_("Основное"), {
            "fields": (
                "teacher",
                "subject",
                "is_primary",
                "is_active",
            )
        }),
        (_("Служебное"), {
            "fields": (
                "created_at",
                "updated_at",
            )
        }),
    )
