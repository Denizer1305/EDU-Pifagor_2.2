from __future__ import annotations

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.feedback.admin.inlines import (
    FeedbackAttachmentInline,
    FeedbackRequestContactInline,
    FeedbackRequestProcessingInline,
    FeedbackRequestTechnicalInline,
    FeedbackStatusHistoryInline,
)
from apps.feedback.models import FeedbackRequest


@admin.register(FeedbackRequest)
class FeedbackRequestAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "uid",
        "subject_display",
        "type",
        "status",
        "source",
        "sender_display",
        "email_display",
        "phone_display",
        "attachments_count_display",
        "consent_display",
        "spam_display",
        "processed_display",
        "processed_by_display",
        "created_at",
    )
    list_display_links = (
        "id",
        "uid",
        "subject_display",
    )
    list_filter = (
        "type",
        "status",
        "source",
        "is_personal_data_consent",
        "created_at",
        "updated_at",
        "processing__is_spam_suspected",
        "processing__processed_at",
    )
    search_fields = (
        "uid",
        "subject",
        "message",
        "user__email",
        "user__profile__last_name",
        "user__profile__first_name",
        "contact__full_name",
        "contact__email",
        "contact__phone",
        "contact__organization_name",
        "technical__error_code",
        "technical__error_title",
        "technical__error_details",
        "technical__page_url",
        "technical__frontend_route",
        "processing__reply_message",
        "processing__internal_note",
        "processing__processed_by__email",
        "processing__assigned_to__email",
    )
    ordering = ("-created_at",)
    readonly_fields = (
        "uid",
        "attachments_count_display",
        "created_at",
        "updated_at",
        "personal_data_consent_at",
    )
    autocomplete_fields = ("user",)
    date_hierarchy = "created_at"
    inlines = [
        FeedbackRequestContactInline,
        FeedbackRequestTechnicalInline,
        FeedbackRequestProcessingInline,
        FeedbackAttachmentInline,
        FeedbackStatusHistoryInline,
    ]

    fieldsets = (
        (
            _("Основное"),
            {
                "fields": (
                    "uid",
                    "user",
                    "type",
                    "status",
                    "source",
                )
            },
        ),
        (
            _("Контент обращения"),
            {
                "fields": (
                    "subject",
                    "message",
                )
            },
        ),
        (
            _("Согласие на обработку данных"),
            {
                "fields": (
                    "is_personal_data_consent",
                    "personal_data_consent_at",
                )
            },
        ),
        (
            _("Служебное"),
            {
                "fields": (
                    "attachments_count_display",
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
            "contact",
            "technical",
            "processing",
            "processing__assigned_to",
            "processing__processed_by",
        )

    @admin.display(description=_("Тема"))
    def subject_display(self, obj: FeedbackRequest) -> str:
        return obj.subject or obj.get_type_display()

    @admin.display(description=_("Отправитель"))
    def sender_display(self, obj: FeedbackRequest) -> str:
        contact = getattr(obj, "contact", None)

        if contact and contact.full_name:
            return contact.full_name

        if obj.user_id:
            return getattr(obj.user, "email", "—")

        return "—"

    @admin.display(description=_("Email"))
    def email_display(self, obj: FeedbackRequest) -> str:
        contact = getattr(obj, "contact", None)

        if contact and contact.email:
            return contact.email

        if obj.user_id:
            return getattr(obj.user, "email", "—")

        return "—"

    @admin.display(description=_("Телефон"))
    def phone_display(self, obj: FeedbackRequest) -> str:
        contact = getattr(obj, "contact", None)
        return contact.phone if contact and contact.phone else "—"

    @admin.display(description=_("Файлы"))
    def attachments_count_display(self, obj: FeedbackRequest) -> int:
        return obj.attachments.count()

    @admin.display(boolean=True, description=_("Согласие"))
    def consent_display(self, obj: FeedbackRequest) -> bool:
        return bool(obj.is_personal_data_consent)

    @admin.display(boolean=True, description=_("Спам"))
    def spam_display(self, obj: FeedbackRequest) -> bool:
        processing = getattr(obj, "processing", None)
        return bool(processing and processing.is_spam_suspected)

    @admin.display(boolean=True, description=_("Обработано"))
    def processed_display(self, obj: FeedbackRequest) -> bool:
        processing = getattr(obj, "processing", None)
        return bool(processing and processing.processed_at)

    @admin.display(description=_("Обработал"))
    def processed_by_display(self, obj: FeedbackRequest) -> str:
        processing = getattr(obj, "processing", None)

        if processing and processing.processed_by_id:
            return getattr(processing.processed_by, "email", "—")

        return "—"
