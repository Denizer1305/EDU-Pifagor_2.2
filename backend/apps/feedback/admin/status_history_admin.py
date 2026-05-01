from __future__ import annotations

from django.contrib import admin

from apps.feedback.models import FeedbackStatusHistory


@admin.register(FeedbackStatusHistory)
class FeedbackStatusHistoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "feedback_request",
        "from_status",
        "to_status",
        "changed_by",
        "created_at",
    )
    list_display_links = (
        "id",
        "feedback_request",
    )
    list_filter = (
        "from_status",
        "to_status",
        "created_at",
    )
    search_fields = (
        "comment",
        "feedback_request__subject",
        "feedback_request__message",
        "changed_by__email",
    )
    ordering = ("-created_at",)
    autocomplete_fields = (
        "feedback_request",
        "changed_by",
    )
    readonly_fields = (
        "created_at",
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related(
            "feedback_request",
            "changed_by",
        )
