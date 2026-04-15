from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from django.utils.translation import gettext_lazy as _

from users.models import (
    User, UserManager, UserRole,
    Role, Profile,
    TeacherProfile, StudentProfile, ParentProfile,
    ParentStudent
)

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User

    list_display = (
        'id', 'email', 'is_email_verified',
        'is_active', 'is_staff',
        'is_superuser', 'created_at', 'updated_at',
    )

    list_filter = (
        'is_active', 'is_staff', 'is_superuser',
        'is_email_verified', 'created_at', 'updated_at',
    )

    search_fields = ("email", "reset_email")
    ordering = ('-created_at',)

    fieldsets = (
        (
            _("Основное"),
            {"fields": ("email", "password")}
        ),
        (
            _("Восстановление"),
            {"fields": ("reset_email")}
        ),
        (
            _("Статусы"),
            {"fields": ("is_email_verified", "is_active", "is_staff", "is_superuser")}
        ),
        (
            _("Права"),
            {"fields": ("groups", "user_permissions")}
        ),
        (
            _("Служебное"),
            {"fields": ("last_login", "created_at", "updated_at")}
        ),
    )

    readonly_fields = ('created_at', 'updated_at', 'last_login')

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "reset_email",
                    "password1",
                    "password2",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
    )

    filter_horizontal = ("groups", "user_permissions")


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "name", "is_active", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("code", "name")
    ordering = ('id',)


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "role", "assigned_at")
    list_filter = ("role", "assigned_at")
    search_fields = ("user__email", "role__code", "role__name")
    autocomplete_fields = ("user", "role")
    ordering = ("-assigned_at",)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "last_name", "first_name", "patronymic", "phone", "city")
    list_filter = ("gender", "city", "created_at")
    search_fields = ("user__email", "last_name", "first_name", "patronymic", "phone")
    autocomplete_fields = ("user",)
    ordering = ("last_name", "first_name")


@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "public_title",
        "experience_years",
        "is_public",
        "show_on_teachers_page",
    )
    list_filter = ("is_public", "show_on_teachers_page", "created_at")
    search_fields = ("user__email", "public_title", "short_bio")
    autocomplete_fields = ("user",)


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "student_code", "admission_year", "status")
    list_filter = ("status", "admission_year", "created_at")
    search_fields = ("user__email", "student_code")
    autocomplete_fields = ("user",)


@admin.register(ParentProfile)
class ParentProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "occupation", "work_place")
    list_filter = ("created_at",)
    search_fields = ("user__email", "occupation", "work_place")
    autocomplete_fields = ("user",)


@admin.register(ParentStudent)
class ParentStudentAdmin(admin.ModelAdmin):
    list_display = ("id", "parent", "student", "relation_type", "is_primary", "created_at")
    list_filter = ("relation_type", "is_primary", "created_at")
    search_fields = (
        "parent__email",
        "student__email",
        "parent__profile__last_name",
        "student__profile__last_name",
    )
    autocomplete_fields = ("parent", "student")
