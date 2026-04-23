from __future__ import annotations

import os

from django.db.models.signals import pre_save
from django.dispatch import receiver

from apps.feedback.models import FeedbackAttachment


def _strip_or_empty(value):
    return value.strip() if isinstance(value, str) else value


@receiver(pre_save, sender=FeedbackAttachment)
def normalize_feedback_attachment_fields(sender, instance, **kwargs):
    instance.original_name = _strip_or_empty(instance.original_name)

    if instance.file and not instance.original_name:
        instance.original_name = os.path.basename(instance.file.name)

    if instance.file:
        instance.file_size = getattr(instance.file, "size", 0) or 0
