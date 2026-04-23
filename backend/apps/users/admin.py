from __future__ import annotations

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from apps.users.models import (
    ParentProfile,
    ParentStudent,
    Profile,
    Role,
    StudentProfile,
    TeacherProfile,
    User,
    UserRole,
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "id", "email",
        "full_name_display", "registration_type",
        "onboarding_status", "email_verified_display",
        "is_active", "is_staff",
        "reviewed_by", "created_at",
    )
    list_display_links = (
        "id", "email",
    )
    list_filter = (
        "registration_type", "onboarding_status",
        "is_active", "is_staff",
        "is_superuser", "created_at",
    )
    search_fields = (
        "email",
        "profile__last_name",
        "profile__first_name",
        "profile__patronymic",
        "review_comment",
    )
    ordering = (
        "-created_at", "email",
    )
    readonly_fields = (
        "created_at", "updated_at",
        "onboarding_completed_at", "reviewed_at",
        "last_login", "email_verified_display",
    )
    autocomplete_fields = (
        "reviewed_by",
    )
    filter_horizontal = (
        "groups", "user_permissions",
    )

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "email", "password",
                )
            },
        ),
        (
            _("Регистрация и онбординг"),
            {
                "fields": (
                    "registration_type",
                    "onboarding_status",
                    "onboarding_completed_at",
                )
            },
        ),
        (
            _("Подтверждение и проверка"),
            {
                "fields": (
                    "email_verified_display",
                    "reset_email",
                    "reviewed_by",
                    "reviewed_at",
                    "review_comment",
                )
            },
        ),
        (
            _("Права доступа"),
            {
                "fields": (
                    "is_active", "is_staff",
                    "is_superuser", "groups",
                    "user_permissions",
                )
            },
        ),
        (
            _("Системная информация"),
            {
                "fields": (
                    "last_login",
                    "created_at", "updated_at",
                )
            },
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1", "password2",
                    "registration_type",
                    "onboarding_status",
                    "is_active", "is_staff",
                    "is_superuser",
                ),
            },
        ),
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related(
            "profile",
            "reviewed_by",
        )

    @admin.display(description=_("ФИО"))
    def full_name_display(self, obj):
        if hasattr(obj, "profile") and obj.profile:
            return obj.profile.full_name
        return "—"

    @admin.display(description=_("Почта подтверждена"), boolean=True)
    def email_verified_display(self, obj):
        return getattr(obj, "is_email_verified", False)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        "id", "user",
        "full_name", "phone",
        "city", "timezone",
        "created_at", "updated_at",
    )
    list_display_links = (
        "id", "user",
    )
    list_filter = (
        "gender", "city",
        "timezone", "created_at",
    )
    search_fields = (
        "user__email",
        "last_name", "first_name",
        "patronymic", "phone",
        "city",
    )
    ordering = (
        "last_name", "first_name",
        "patronymic",
    )
    readonly_fields = (
        "created_at", "updated_at",
        "full_name", "short_name",
    )
    autocomplete_fields = (
        "user",
    )

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "user",
                    "last_name", "first_name",
                    "patronymic",
                )
            },
        ),
        (
            _("Контактные данные"),
            {
                "fields": (
                    "phone", "birth_date",
                    "gender", "city",
                    "timezone",
                )
            },
        ),
        (
            _("Публичные данные"),
            {
                "fields": (
                    "avatar",
                    "about",
                    "social_link_max",
                    "social_link_vk",
                )
            },
        ),
        (
            _("Служебные поля"),
            {
                "fields": (
                    "full_name", "short_name",
                    "created_at", "updated_at",
                )
            },
        ),
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related("user")


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = (
        "id", "code",
        "name", "description",
        "is_active", "created_at",
        "updated_at",
    )
    list_display_links = (
        "id", "code",
    )
    list_filter = (
        "is_active", "created_at",
    )
    search_fields = (
        "code", "name",
        "description",
    )
    ordering = (
        "name", "code",
    )
    readonly_fields = (
        "created_at", "updated_at",
    )

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "code", "name",
                    "description", "is_active",
                )
            },
        ),
        (
            _("Системная информация"),
            {
                "fields": (
                    "created_at", "updated_at",
                )
            },
        ),
    )


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = (
        "id", "user",
        "user_email", "role",
        "assigned_at",
    )
    list_display_links = (
        "id", "user",
    )
    list_filter = (
        "role", "assigned_at",
    )
    search_fields = (
        "user__email",
        "role__code",
        "role__name",
    )
    ordering = (
        "-assigned_at",
    )
    readonly_fields = (
        "assigned_at",
    )
    autocomplete_fields = (
        "user", "role",
    )

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "user", "role",
                )
            },
        ),
        (
            _("Системная информация"),
            {
                "fields": (
                    "assigned_at",
                )
            },
        ),
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related(
            "user", "role",
        )

    @admin.display(description=_("Email"))
    def user_email(self, obj):
        return obj.user.email


@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = (
        "id", "user",
        "full_name_display",
        "requested_organization",
        "requested_department",
        "verification_status",
        "verified_by", "verified_at",
    )
    list_display_links = (
        "id", "user",
    )
    list_filter = (
        "verification_status",
        "requested_organization",
        "requested_department",
        "verified_at",
    )
    search_fields = (
        "user__email",
        "user__profile__last_name",
        "user__profile__first_name",
        "specialization",
        "verification_comment",
    )
    ordering = (
        "user__profile__last_name",
        "user__profile__first_name",
    )
    readonly_fields = (
        "code_verified_at",
        "verified_at",
        "created_at", "updated_at",
    )
    autocomplete_fields = (
        "user",
        "requested_organization",
        "requested_department",
        "verified_by",
    )

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "user",
                    "specialization",
                    "education",
                )
            },
        ),
        (
            _("Организационный запрос"),
            {
                "fields": (
                    "requested_organization",
                    "requested_department",
                )
            },
        ),
        (
            _("Подтверждение"),
            {
                "fields": (
                    "verification_status",
                    "code_verified_at",
                    "verified_by",
                    "verified_at",
                    "verification_comment",
                )
            },
        ),
        (
            _("Системная информация"),
            {
                "fields": (
                    "created_at", "updated_at",
                )
            },
        ),
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related(
            "user",
            "user__profile",
            "requested_organization",
            "requested_department",
            "verified_by",
        )

    @admin.display(description=_("ФИО"))
    def full_name_display(self, obj: TeacherProfile) -> str:
        if hasattr(obj.user, "profile") and obj.user.profile:
            return obj.user.profile.full_name
        return obj.user.email


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = (
        "id", "user",
        "full_name_display",
        "requested_organization",
        "requested_department",
        "requested_group",
        "verification_status",
        "verified_by", "verified_at",
    )
    list_display_links = (
        "id", "user",
    )
    list_filter = (
        "verification_status",
        "requested_organization",
        "requested_department",
        "requested_group",
        "verified_at",
    )
    search_fields = (
        "user__email",
        "user__profile__last_name",
        "user__profile__first_name",
        "student_code",
        "submitted_group_code",
        "verification_comment",
    )
    ordering = (
        "user__profile__last_name",
        "user__profile__first_name",
    )
    readonly_fields = (
        "verified_at",
        "created_at", "updated_at",
    )
    autocomplete_fields = (
        "user",
        "requested_organization",
        "requested_department",
        "requested_group",
        "verified_by",
    )

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "user",
                    "student_code",
                )
            },
        ),
        (
            _("Учебный запрос"),
            {
                "fields": (
                    "requested_organization",
                    "requested_department",
                    "requested_group",
                    "submitted_group_code",
                )
            },
        ),
        (
            _("Подтверждение"),
            {
                "fields": (
                    "verification_status",
                    "verified_by",
                    "verified_at",
                    "verification_comment",
                )
            },
        ),
        (
            _("Системная информация"),
            {
                "fields": (
                    "created_at", "updated_at",
                )
            },
        ),
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related(
            "user",
            "user__profile",
            "requested_organization",
            "requested_department",
            "requested_group",
            "verified_by",
        )

    @admin.display(description=_("ФИО"))
    def full_name_display(self, obj: StudentProfile) -> str:
        if hasattr(obj.user, "profile") and obj.user.profile:
            return obj.user.profile.full_name
        return obj.user.email


@admin.register(ParentProfile)
class ParentProfileAdmin(admin.ModelAdmin):
    list_display = (
        "id", "user",
        "full_name_display",
        "work_place",
        "created_at", "updated_at",
    )
    list_display_links = (
        "id", "user",
    )
    search_fields = (
        "user__email",
        "user__profile__last_name",
        "user__profile__first_name",
        "work_place",
    )
    ordering = (
        "user__profile__last_name",
        "user__profile__first_name",
    )
    readonly_fields = (
        "created_at", "updated_at",
    )
    autocomplete_fields = (
        "user",
    )

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "user",
                    "work_place",
                )
            },
        ),
        (
            _("Системная информация"),
            {
                "fields": (
                    "created_at", "updated_at",
                )
            },
        ),
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related(
            "user",
            "user__profile",
        )

    @admin.display(description=_("ФИО"))
    def full_name_display(self, obj: ParentProfile) -> str:
        if hasattr(obj.user, "profile") and obj.user.profile:
            return obj.user.profile.full_name
        return obj.user.email


@admin.register(ParentStudent)
class ParentStudentAdmin(admin.ModelAdmin):
    list_display = (
        "id", "parent",
        "student", "relation_type",
        "status", "requested_by",
        "approved_by", "approved_at",
        "created_at",
    )
    list_display_links = (
        "id", "parent",
    )
    list_filter = (
        "relation_type",
        "status",
        "approved_at",
        "created_at",
    )
    search_fields = (
        "parent__email",
        "parent__profile__last_name",
        "student__email",
        "student__profile__last_name",
        "comment",
    )
    ordering = (
        "-created_at",
    )
    readonly_fields = (
        "approved_at",
        "created_at",
    )
    autocomplete_fields = (
        "parent",
        "student",
        "requested_by",
        "approved_by",
    )

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "parent",
                    "student",
                    "relation_type",
                    "status",
                )
            },
        ),
        (
            _("Подтверждение"),
            {
                "fields": (
                    "requested_by",
                    "approved_by",
                    "approved_at",
                    "comment",
                )
            },
        ),
        (
            _("Системная информация"),
            {
                "fields": (
                    "created_at",
                )
            },
        ),
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related(
            "parent",
            "parent__profile",
            "student",
            "student__profile",
            "requested_by",
            "approved_by",
        )
