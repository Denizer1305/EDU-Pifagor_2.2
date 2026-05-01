from __future__ import annotations

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.feedback.models import FeedbackRequestProcessing


@admin.register(FeedbackRequestProcessing)
class FeedbackRequestProcessingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "feedback_request",
        "assigned_to",
        "assigned_at",
        "processed_by",
        "processed_at",
        "is_processed_display",
        "is_spam_suspected",
        "created_at",
    )
    list_display_links = (
        "id",
        "feedback_request",
    )
    list_filter = (
        "is_spam_suspected",
        "assigned_at",
        "processed_at",
        "created_at",
    )
    search_fields = (
        "reply_message",
        "internal_note",
        "feedback_request__subject",
        "feedback_request__message",
        "assigned_to__email",
        "processed_by__email",
    )
    ordering = ("-created_at",)
    autocomplete_fields = (
        "feedback_request",
        "assigned_to",
        "processed_by",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (_("Основное"), {
            "fields": (
                "feedback_request",
                "assigned_to",
                "assigned_at",
                "processed_by",
                "processed_at",
            )
        }),
        (_("Ответ и заметки"), {
            "fields": (
                "reply_message",
                "internal_note",
            )
        }),
        (_("Антиспам"), {
            "fields": (
                "is_spam_suspected",
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
        return queryset.select_related(
            "feedback_request",
            "assigned_to",
            "processed_by",
        )

    @admin.display(boolean=True, description=_("Обработано"))
    def is_processed_display(self, obj: FeedbackRequestProcessing) -> bool:
        return obj.is_processed
