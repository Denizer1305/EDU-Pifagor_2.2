from __future__ import annotations

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class FeedbackRequest(models.Model):
    class TypeChoices(models.TextChoices):
        QUESTION = "question", _("Вопрос")
        SUGGESTION = "suggestion", _("Предложение")
        BUG = "bug", _("Сообщение об ошибке")
        COMPLAINT = "complaint", _("Жалоба")
        COOPERATION = "cooperation", _("Сотрудничество")
        CALLBACK = "callback", _("Обратный звонок")
        OTHER = "other", _("Другое")

    class StatusChoices(models.TextChoices):
        NEW = "new", _("Новое")
        IN_PROGRESS = "in_progress", _("В обработке")
        WAITING_FOR_USER = "waiting_for_user", _("Ожидает ответа пользователя")
        RESOLVED = "resolved", _("Решено")
        REJECTED = "rejected", _("Отклонено")
        SPAM = "spam", _("Спам")
        ARCHIVED = "archived", _("Архивировано")

    class SourceChoices(models.TextChoices):
        CONTACTS_PAGE = "contacts_page", _("Страница контактов")
        ERROR_MODAL = "error_modal", _("Модальное окно ошибки")
        SUPPORT_WIDGET = "support_widget", _("Виджет поддержки")
        FOOTER = "footer", _("Футер")
        ADMIN_PANEL = "admin_panel", _("Админ-панель")
        API = "api", _("API")
        OTHER = "other", _("Другое")

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="feedback_requests",
        verbose_name=_("Пользователь"),
        null=True,
        blank=True,
    )

    type = models.CharField(
        _("Тип обращения"),
        max_length=32,
        choices=TypeChoices.choices,
        default=TypeChoices.QUESTION,
    )
    status = models.CharField(
        _("Статус"),
        max_length=32,
        choices=StatusChoices.choices,
        default=StatusChoices.NEW,
    )
    source = models.CharField(
        _("Источник"),
        max_length=32,
        choices=SourceChoices.choices,
        default=SourceChoices.CONTACTS_PAGE,
    )

    subject = models.CharField(
        _("Тема"),
        max_length=255,
        blank=True,
    )
    message = models.TextField(
        _("Сообщение"),
        validators=[MinLengthValidator(5)],
    )

    full_name = models.CharField(
        _("Имя отправителя"),
        max_length=255,
        blank=True,
    )
    email = models.EmailField(
        _("Email отправителя"),
        blank=True,
    )
    phone = models.CharField(
        _("Телефон отправителя"),
        max_length=32,
        blank=True,
    )
    organization_name = models.CharField(
        _("Организация"),
        max_length=255,
        blank=True,
    )

    is_personal_data_consent = models.BooleanField(
        _("Согласие на обработку персональных данных"),
        default=False,
    )
    personal_data_consent_at = models.DateTimeField(
        _("Дата согласия на обработку персональных данных"),
        null=True,
        blank=True,
    )

    page_url = models.URLField(
        _("URL страницы"),
        blank=True,
    )
    frontend_route = models.CharField(
        _("Маршрут фронтенда"),
        max_length=255,
        blank=True,
    )
    error_code = models.CharField(
        _("Код ошибки"),
        max_length=100,
        blank=True,
    )
    error_title = models.CharField(
        _("Краткий заголовок ошибки"),
        max_length=255,
        blank=True,
    )
    error_details = models.TextField(
        _("Технические детали ошибки"),
        blank=True,
    )
    client_platform = models.CharField(
        _("Платформа клиента"),
        max_length=100,
        blank=True,
    )
    app_version = models.CharField(
        _("Версия приложения"),
        max_length=100,
        blank=True,
    )

    is_processed = models.BooleanField(
        _("Обработано"),
        default=False,
    )
    processed_at = models.DateTimeField(
        _("Дата обработки"),
        null=True,
        blank=True,
    )
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="processed_feedback_requests",
        verbose_name=_("Обработал"),
        null=True,
        blank=True,
    )
    reply_message = models.TextField(
        _("Комментарий / ответ"),
        blank=True,
    )
    internal_note = models.TextField(
        _("Внутренняя заметка"),
        blank=True,
    )

    is_spam_suspected = models.BooleanField(
        _("Подозрение на спам"),
        default=False,
    )
    ip_address = models.GenericIPAddressField(
        _("IP-адрес"),
        null=True,
        blank=True,
    )
    user_agent = models.TextField(
        _("User-Agent"),
        blank=True,
    )
    referrer = models.URLField(
        _("Referrer"),
        blank=True,
    )

    created_at = models.DateTimeField(
        _("Дата создания"),
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        _("Дата обновления"),
        auto_now=True,
    )

    class Meta:
        db_table = "feedback_request"
        verbose_name = _("Обращение")
        verbose_name_plural = _("Обращения")
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=("status", "created_at"), name="feedback_status_created_idx"),
            models.Index(fields=("type", "created_at"), name="feedback_type_created_idx"),
            models.Index(fields=("source", "created_at"), name="feedback_source_created_idx"),
            models.Index(fields=("email",), name="feedback_email_idx"),
            models.Index(fields=("created_at",), name="feedback_created_idx"),
        ]

    def __str__(self) -> str:
        base = self.subject or self.get_type_display()
        sender = self.full_name or self.email or _("Без имени")
        return f"{base} — {sender}"

    @property
    def attachments_count(self) -> int:
        return self.attachments.count()

    def clean(self) -> None:
        super().clean()

        errors: dict[str, str] = {}

        self.subject = (self.subject or "").strip()
        self.message = (self.message or "").strip()
        self.full_name = (self.full_name or "").strip()
        self.email = (self.email or "").strip()
        self.phone = (self.phone or "").strip()
        self.organization_name = (self.organization_name or "").strip()
        self.page_url = (self.page_url or "").strip()
        self.frontend_route = (self.frontend_route or "").strip()
        self.error_code = (self.error_code or "").strip()
        self.error_title = (self.error_title or "").strip()
        self.error_details = (self.error_details or "").strip()
        self.client_platform = (self.client_platform or "").strip()
        self.app_version = (self.app_version or "").strip()
        self.reply_message = (self.reply_message or "").strip()
        self.internal_note = (self.internal_note or "").strip()
        self.user_agent = (self.user_agent or "").strip()
        self.referrer = (self.referrer or "").strip()

        if not self.message:
            errors["message"] = _("Сообщение не может быть пустым.")

        if self.source == self.SourceChoices.CONTACTS_PAGE and not self.email:
            errors["email"] = _("Для формы контактов необходимо указать email.")

        if not self.is_personal_data_consent:
            errors["is_personal_data_consent"] = _(
                "Необходимо согласие на обработку персональных данных."
            )

        if self.is_personal_data_consent and not self.personal_data_consent_at:
            self.personal_data_consent_at = timezone.now()

        if self.source == self.SourceChoices.ERROR_MODAL:
            if not self.type:
                self.type = self.TypeChoices.BUG

        if self.is_processed and not self.processed_at:
            errors["processed_at"] = _(
                "Для обработанного обращения нужно указать дату обработки."
            )

        if self.processed_at and not self.processed_by:
            errors["processed_by"] = _(
                "Если указана дата обработки, нужно указать, кто обработал обращение."
            )

        if self.status == self.StatusChoices.RESOLVED and not self.is_processed:
            errors["status"] = _(
                "Решённое обращение должно быть отмечено как обработанное."
            )

        if self.status == self.StatusChoices.SPAM:
            self.is_spam_suspected = True

        if len(self.error_details) > 10000:
            errors["error_details"] = _(
                "Технические детали ошибки не должны превышать 10000 символов."
            )

        if errors:
            raise ValidationError(errors)
