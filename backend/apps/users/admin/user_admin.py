from __future__ import annotations

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from apps.users.admin.helpers import get_user_full_name_or_email
from apps.users.models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "id",
        "email",
        "full_name_display",
        "registration_type",
        "onboarding_status",
        "email_verified_display",
        "is_active",
        "is_staff",
        "reviewed_by",
        "created_at",
    )
    list_display_links = (
        "id",
        "email",
    )
    list_filter = (
        "registration_type",
        "onboarding_status",
        "is_active",
        "is_staff",
        "is_superuser",
        "created_at",
    )
    search_fields = (
        "email",
        "profile__last_name",
        "profile__first_name",
        "profile__patronymic",
        "review_comment",
    )
    ordering = (
        "-created_at",
        "email",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
        "onboarding_completed_at",
        "reviewed_at",
        "last_login",
        "email_verified_display",
    )
    autocomplete_fields = ("reviewed_by",)
    filter_horizontal = (
        "groups",
        "user_permissions",
    )

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "email",
                    "password",
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
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (
            _("Системная информация"),
            {
                "fields": (
                    "last_login",
                    "created_at",
                    "updated_at",
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
                    "password1",
                    "password2",
                    "registration_type",
                    "onboarding_status",
                    "is_active",
                    "is_staff",
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
    def full_name_display(self, obj: User) -> str:
        return get_user_full_name_or_email(obj)

    @admin.display(description=_("Почта подтверждена"), boolean=True)
    def email_verified_display(self, obj: User) -> bool:
        return getattr(obj, "is_email_verified", False)
