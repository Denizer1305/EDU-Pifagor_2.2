from __future__ import annotations

import os

from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone

from apps.feedback.models import FeedbackAttachment, FeedbackRequest


def _strip_or_empty(value):
    return value.strip() if isinstance(value, str) else value


@receiver(pre_save, sender=FeedbackRequest)
def normalize_feedback_request_fields(sender, instance, **kwargs):
    instance.subject = _strip_or_empty(instance.subject)
    instance.message = _strip_or_empty(instance.message)
    instance.full_name = _strip_or_empty(instance.full_name)
    instance.email = _strip_or_empty(instance.email)
    instance.phone = _strip_or_empty(instance.phone)
    instance.organization_name = _strip_or_empty(instance.organization_name)
    instance.page_url = _strip_or_empty(instance.page_url)
    instance.frontend_route = _strip_or_empty(instance.frontend_route)
    instance.error_code = _strip_or_empty(instance.error_code)
    instance.error_title = _strip_or_empty(instance.error_title)
    instance.error_details = _strip_or_empty(instance.error_details)
    instance.client_platform = _strip_or_empty(instance.client_platform)
    instance.app_version = _strip_or_empty(instance.app_version)
    instance.reply_message = _strip_or_empty(instance.reply_message)
    instance.internal_note = _strip_or_empty(instance.internal_note)
    instance.user_agent = _strip_or_empty(instance.user_agent)
    instance.referrer = _strip_or_empty(instance.referrer)

    if instance.is_personal_data_consent and not instance.personal_data_consent_at:
        instance.personal_data_consent_at = timezone.now()

    if instance.status == FeedbackRequest.StatusChoices.SPAM:
        instance.is_spam_suspected = True

    if instance.status == FeedbackRequest.StatusChoices.RESOLVED and not instance.is_processed:
        instance.is_processed = True

    if instance.is_processed and instance.processed_at is None:
        instance.processed_at = timezone.now()


@receiver(pre_save, sender=FeedbackAttachment)
def normalize_feedback_attachment_fields(sender, instance, **kwargs):
    instance.original_name = _strip_or_empty(instance.original_name)

    if instance.file and not instance.original_name:
        instance.original_name = os.path.basename(instance.file.name)

    if instance.file:
        instance.file_size = getattr(instance.file, "size", 0) or 0
