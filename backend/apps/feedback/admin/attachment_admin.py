from __future__ import annotations

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.feedback.models import FeedbackAttachment


@admin.register(FeedbackAttachment)
class FeedbackAttachmentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "feedback_request",
        "original_name",
        "kind",
        "mime_type",
        "file_size",
        "created_at",
    )
    list_display_links = (
        "id",
        "original_name",
    )
    list_filter = (
        "kind",
        "mime_type",
        "created_at",
    )
    search_fields = (
        "original_name",
        "feedback_request__subject",
        "feedback_request__message",
        "feedback_request__contact__email",
        "feedback_request__contact__full_name",
    )
    ordering = ("-created_at",)
    autocomplete_fields = (
        "feedback_request",
    )
    readonly_fields = (
        "original_name",
        "kind",
        "mime_type",
        "file_size",
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (_("Основное"), {
            "fields": (
                "feedback_request",
                "file",
                "original_name",
            )
        }),
        (_("Метаданные файла"), {
            "fields": (
                "kind",
                "mime_type",
                "file_size",
            )
        }),
        (_("Служебное"), {
            "fields": (
                "created_at",
                "updated_at",
            )
        }),
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related("feedback_request")
