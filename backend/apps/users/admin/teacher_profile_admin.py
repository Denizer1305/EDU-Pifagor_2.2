from __future__ import annotations

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.users.admin.helpers import get_user_full_name_or_email
from apps.users.models import TeacherProfile


@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "full_name_display",
        "requested_organization",
        "requested_department",
        "verification_status",
        "verified_by",
        "verified_at",
    )
    list_display_links = (
        "id",
        "user",
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
        "created_at",
        "updated_at",
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
                    "created_at",
                    "updated_at",
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
        return get_user_full_name_or_email(obj.user)
