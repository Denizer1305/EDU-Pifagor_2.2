from __future__ import annotations

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.users.admin.helpers import get_user_full_name_or_email
from apps.users.models import StudentProfile


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "full_name_display",
        "requested_organization",
        "requested_department",
        "requested_group",
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
        "created_at",
        "updated_at",
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
            "requested_group",
            "verified_by",
        )

    @admin.display(description=_("ФИО"))
    def full_name_display(self, obj: StudentProfile) -> str:
        return get_user_full_name_or_email(obj.user)
