from __future__ import annotations

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.feedback.models import FeedbackAttachment, FeedbackRequest


class FeedbackAttachmentInline(admin.TabularInline):
    model = FeedbackAttachment
    extra = 0
    fields = (
        "file",
        "original_name",
        "file_type",
        "file_size",
        "created_at",
    )
    readonly_fields = (
        "original_name",
        "file_type",
        "file_size",
        "created_at",
    )
    show_change_link = True


@admin.register(FeedbackRequest)
class FeedbackRequestAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "subject_display",
        "type",
        "status",
        "source",
        "sender_display",
        "email",
        "phone",
        "attachments_count_display",
        "is_personal_data_consent",
        "is_spam_suspected",
        "is_processed",
        "processed_by",
        "created_at",
    )
    list_display_links = (
        "id",
        "subject_display",
    )
    list_filter = (
        "type",
        "status",
        "source",
        "is_personal_data_consent",
        "is_spam_suspected",
        "is_processed",
        "created_at",
        "processed_at",
    )
    search_fields = (
        "subject",
        "message",
        "full_name",
        "email",
        "phone",
        "organization_name",
        "error_code",
        "error_title",
        "error_details",
        "reply_message",
        "internal_note",
        "user__email",
        "user__profile__last_name",
        "user__profile__first_name",
        "processed_by__email",
    )
    ordering = (
        "-created_at",
    )
    readonly_fields = (
        "attachments_count_display",
        "personal_data_consent_at",
        "created_at",
        "updated_at",
    )
    autocomplete_fields = (
        "user",
        "processed_by",
    )
    list_select_related = (
        "user",
        "processed_by",
    )
    inlines = [FeedbackAttachmentInline]
    date_hierarchy = "created_at"

    fieldsets = (
        (_("Основное"), {
            "fields": (
                "user",
                "type",
                "status",
                "source",
            )
        }),
        (_("Контент обращения"), {
            "fields": (
                "subject",
                "message",
            )
        }),
        (_("Контактные данные"), {
            "fields": (
                "full_name",
                "email",
                "phone",
                "organization_name",
            )
        }),
        (_("Согласие на обработку данных"), {
            "fields": (
                "is_personal_data_consent",
                "personal_data_consent_at",
            )
        }),
        (_("Технический контекст ошибки"), {
            "classes": ("collapse",),
            "fields": (
                "page_url",
                "frontend_route",
                "error_code",
                "error_title",
                "error_details",
                "client_platform",
                "app_version",
            )
        }),
        (_("Обработка"), {
            "fields": (
                "is_processed",
                "processed_at",
                "processed_by",
                "reply_message",
                "internal_note",
            )
        }),
        (_("Антиспам и тех. данные"), {
            "classes": ("collapse",),
            "fields": (
                "is_spam_suspected",
                "ip_address",
                "user_agent",
                "referrer",
            )
        }),
        (_("Служебное"), {
            "fields": (
                "attachments_count_display",
                "created_at",
                "updated_at",
            )
        }),
    )

    @admin.display(description=_("Тема"))
    def subject_display(self, obj: FeedbackRequest) -> str:
        return obj.subject or obj.get_type_display()

    @admin.display(description=_("Отправитель"))
    def sender_display(self, obj: FeedbackRequest) -> str:
        if obj.full_name:
            return obj.full_name
        if obj.user_id:
            return getattr(obj.user, "email", "—")
        return "—"

    @admin.display(description=_("Файлы"))
    def attachments_count_display(self, obj: FeedbackRequest) -> int:
        return obj.attachments.count()


@admin.register(FeedbackAttachment)
class FeedbackAttachmentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "feedback_request",
        "original_name",
        "file_type",
        "file_size",
        "created_at",
    )
    list_display_links = (
        "id",
        "original_name",
    )
    list_filter = (
        "file_type",
        "created_at",
    )
    search_fields = (
        "original_name",
        "feedback_request__subject",
        "feedback_request__message",
        "feedback_request__email",
        "feedback_request__full_name",
    )
    ordering = (
        "-created_at",
    )
    autocomplete_fields = (
        "feedback_request",
    )
    readonly_fields = (
        "original_name",
        "file_type",
        "file_size",
        "created_at",
    )
    list_select_related = (
        "feedback_request",
    )
