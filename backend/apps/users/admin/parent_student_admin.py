from __future__ import annotations

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.users.models import ParentStudent


@admin.register(ParentStudent)
class ParentStudentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "parent",
        "student",
        "relation_type",
        "status",
        "requested_by",
        "approved_by",
        "approved_at",
        "created_at",
    )
    list_display_links = (
        "id",
        "parent",
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
    ordering = ("-created_at",)
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
            {"fields": ("created_at",)},
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
