from __future__ import annotations

from django.contrib import admin

from apps.feedback.models import (
    FeedbackAttachment,
    FeedbackRequestContact,
    FeedbackRequestProcessing,
    FeedbackRequestTechnical,
    FeedbackStatusHistory,
)


class FeedbackRequestContactInline(admin.StackedInline):
    model = FeedbackRequestContact
    extra = 0
    max_num = 1
    can_delete = False
    autocomplete_fields = ()
    fields = (
        "full_name",
        "email",
        "phone",
        "organization_name",
        "created_at",
        "updated_at",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )


class FeedbackRequestTechnicalInline(admin.StackedInline):
    model = FeedbackRequestTechnical
    extra = 0
    max_num = 1
    can_delete = False
    classes = ("collapse",)
    fields = (
        "page_url",
        "frontend_route",
        "error_code",
        "error_title",
        "error_details",
        "client_platform",
        "app_version",
        "ip_address",
        "user_agent",
        "referrer",
        "extra_payload",
        "created_at",
        "updated_at",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )


class FeedbackRequestProcessingInline(admin.StackedInline):
    model = FeedbackRequestProcessing
    extra = 0
    max_num = 1
    can_delete = False
    autocomplete_fields = (
        "assigned_to",
        "processed_by",
    )
    fields = (
        "assigned_to",
        "assigned_at",
        "processed_by",
        "processed_at",
        "reply_message",
        "internal_note",
        "is_spam_suspected",
        "created_at",
        "updated_at",
    )
    readonly_fields = (
        "assigned_at",
        "created_at",
        "updated_at",
    )


class FeedbackAttachmentInline(admin.TabularInline):
    model = FeedbackAttachment
    extra = 0
    fields = (
        "file",
        "original_name",
        "kind",
        "mime_type",
        "file_size",
        "created_at",
    )
    readonly_fields = (
        "original_name",
        "kind",
        "mime_type",
        "file_size",
        "created_at",
    )
    show_change_link = True


class FeedbackStatusHistoryInline(admin.TabularInline):
    model = FeedbackStatusHistory
    extra = 0
    autocomplete_fields = (
        "changed_by",
    )
    fields = (
        "from_status",
        "to_status",
        "comment",
        "changed_by",
        "created_at",
    )
    readonly_fields = (
        "created_at",
    )
    ordering = ("-created_at",)
