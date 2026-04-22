from __future__ import annotations

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.feedback.models import (
    FeedbackAttachment,
    FeedbackRequest,
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
    autocomplete_fields = (
        "user",
    )
    date_hierarchy = "created_at"
    inlines = [
        FeedbackRequestContactInline,
        FeedbackRequestTechnicalInline,
        FeedbackRequestProcessingInline,
        FeedbackAttachmentInline,
        FeedbackStatusHistoryInline,
    ]

    fieldsets = (
        (_("Основное"), {
            "fields": (
                "uid",
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
        (_("Согласие на обработку данных"), {
            "fields": (
                "is_personal_data_consent",
                "personal_data_consent_at",
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
    autocomplete_fields = (
        "feedback_request",
    )
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
    autocomplete_fields = (
        "feedback_request",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related("feedback_request")


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
