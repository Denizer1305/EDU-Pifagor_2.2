from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.organizations.models import (
    OrganizationType,
    Organization,
    Department,
    Group,
    GroupCurator,
    Subject,
    SubjectCategory,
    TeacherOrganization,
    TeacherSubject
)


@admin.register(OrganizationType)
class OrganizationTypeAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name',
        'code', 'is_active',
        'created_at',
    )
    list_filter = (
        'is_active', 'created_at',
    )
    search_fields = (
        'name', 'code',
    )
    ordering = (
        'name',
    )


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name',
        'short_name', 'type',
        'city', 'email',
        'phone', 'is_active',
        'created_at',
    )
    list_filter = (
        'type', 'city',
        'is_active', 'created_at',
    )
    search_fields = (
        'name', 'short_name',
        'city', 'email',
        'phone', 'address',
    )
    autocomplete_fields = (
        'type',
    )
    ordering = (
        'name',
    )

    fieldsets = (
        (_("Основное"), {
            'fields': (
                'name', 'short_name',
                'type', 'description',
            )
        }), (_("Контактные данные"), {
            'fields': (
                'city',
                'address',
                'phone',
                'email',
                'website',
            )
        }),
        (_("Медиа"), {
            'fields': (
                'logo',
            )
        }), (_("Статус"), {
            'fields': (
                'is_active',
            )
        }),
        (_("Служебное"), {
            'fields': (
                'created_at',
                'updated_at',
            )
        }),
    )
    readonly_fields = (
        'created_at', 'updated_at',
    )


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name',
        'short_name', 'organization',
        'is_active', 'created_at',
    )
    list_filter = (
        'organization', 'is_active',
        'created_at',
    )
    search_fields = (
        'name', 'short_name',
        'organization__name', 'organization__short_name',
    )
    autocomplete_fields = (
        'organization',
    )
    ordering = (
        'organization', 'name',
    )


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name',
        'code', 'organization',
        'department', 'study_form',
        'course_number', 'academic_year',
        'is_active', 'created_at',
    )
    list_filter = (
        'organization', 'department',
        'study_form', 'status',
        'admission_year', 'graduation_year',
        'academic_year', 'created_at',
    )
    search_fields = (
        'name', 'code',
        'organization__name', 'organization__short_name',
        'department__name',
    )
    autocomplete_fields = (
        'organization', 'department',
    )
    ordering = (
        'organization', 'name',
    )

    fieldsets = (
        (_("Основное"), {
            'fields': (
                'organization',
                'department',
                'name',
                'code',
                'description',
            )
        }), (_("Учебные параметры"), {
            'fields': (
                'study_form',
                'course_number',
                'admission_year',
                'graduation_year',
                'academic_year',
                'status',
            )
        }),
        (_("Статус"), {
            'fields': (
                'is_active',
            )
        }), (_("Служебное"), {
            'fields': (
                'created_at',
                'updated_at',
            )
        }),
    )
    readonly_fields = (
        'created_at', 'updated_at',
    )


@admin.register(GroupCurator)
class GroupCuratorAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'group',
        'teacher', 'is_primary',
        'starts_at', 'ends_at',
        'created_at',
    )
    list_filter = (
        'is_primary', 'starts_at',
        'ends_at', 'created_at',
    )
    search_fields = (
        'group__name', 'group__code',
        'teacher__email', 'teacher__profile__last_name',
        'teacher__profile__first_name',
    )
    autocomplete_fields = (
        'group', 'teacher',
    )
    ordering = (
        '-is_primary', '-starts_at',
        '-created_at',
    )


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name',
        'short_name', 'category',
        'is_active', 'created_at',
    )
    list_filter = (
        'category', 'is_active',
        'created_at',
    )
    search_fields = (
        'name', 'short_name',
        'category__name', 'category__code',
    )
    autocomplete_fields = (
        'category',
    )
    ordering = (
        'name',
    )


@admin.register(SubjectCategory)
class SubjectCategoryAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name',
        'code', 'is_active',
        'created_at',
    )
    list_filter = (
        'is_active', 'created_at',
    )
    search_fields = (
        'name', 'code',
    )
    ordering = (
        'name',
    )


@admin.register(TeacherOrganization)
class TeacherOrganizationAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'teacher',
        'organization', 'employment_type',
        'is_primary', 'is_active',
        'starts_at', 'ends_at',
        'created_at',
    )
    list_filter = (
        'employment_type', 'is_primary',
        'is_active', 'starts_at',
        'ends_at', 'created_at',
    )
    search_fields = (
        'teacher__email', 'teacher__profile__last_name',
        'teacher__profile__first_name', 'organization__name',
        'organization__short_name',
    )
    autocomplete_fields = (
        'teacher', 'organization',
    )
    ordering = (
        'teacher', 'organization',
    )


@admin.register(TeacherSubject)
class TeacherSubjectAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'teacher',
        'subject', 'is_primary',
        'is_active', 'created_at',
    )
    list_filter = (
        'is_primary', 'is_active',
        'subject__category', 'created_at',
    )
    search_fields = (
        'teacher__email', 'teacher__profile__last_name',
        'teacher__profile__first_name', 'subject__name',
        'subject__short_name', 'subject__category__name',
    )
    autocomplete_fields = (
        'teacher', 'subject',
    )
    ordering = (
        'teacher', 'subject',
    )
