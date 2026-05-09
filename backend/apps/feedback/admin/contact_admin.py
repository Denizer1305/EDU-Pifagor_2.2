from __future__ import annotations

from django.contrib import admin

from apps.feedback.models import FeedbackRequestContact


@admin.register(FeedbackRequestContact)
class FeedbackRequestContactAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "feedback_request",
        "full_name",
        "email",
        "phone",
        "organization_name",
        "created_at",
    )
    list_display_links = (
        "id",
        "feedback_request",
    )
    search_fields = (
        "full_name",
        "email",
        "phone",
        "organization_name",
        "feedback_request__subject",
        "feedback_request__message",
        "feedback_request__user__email",
    )
    ordering = ("-created_at",)
    autocomplete_fields = ("feedback_request",)
    readonly_fields = (
        "created_at",
        "updated_at",
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related(
            "feedback_request",
            "feedback_request__user",
        )
