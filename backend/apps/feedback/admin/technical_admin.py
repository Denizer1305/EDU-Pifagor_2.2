from __future__ import annotations

from django.contrib import admin

from apps.feedback.models import FeedbackRequestTechnical


@admin.register(FeedbackRequestTechnical)
class FeedbackRequestTechnicalAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "feedback_request",
        "error_code",
        "error_title",
        "client_platform",
        "app_version",
        "created_at",
    )
    list_display_links = (
        "id",
        "feedback_request",
    )
    list_filter = (
        "client_platform",
        "app_version",
        "created_at",
    )
    search_fields = (
        "error_code",
        "error_title",
        "error_details",
        "page_url",
        "frontend_route",
        "feedback_request__subject",
        "feedback_request__message",
    )
    ordering = ("-created_at",)
    autocomplete_fields = ("feedback_request",)
    readonly_fields = (
        "created_at",
        "updated_at",
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related("feedback_request")
