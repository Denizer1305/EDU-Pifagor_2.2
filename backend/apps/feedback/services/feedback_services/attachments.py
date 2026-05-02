from __future__ import annotations

import logging
from collections.abc import Iterable

from django.core.exceptions import ValidationError

from apps.feedback.models import FeedbackAttachment, FeedbackRequest
from apps.feedback.services.feedback_services.constants import (
    MAX_ATTACHMENTS_PER_REQUEST,
)

logger = logging.getLogger(__name__)


def _validate_attachments_payload(files: Iterable | None) -> list:
    """Проверяет количество вложений обращения."""

    if not files:
        return []

    files_list = list(files)
    if len(files_list) > MAX_ATTACHMENTS_PER_REQUEST:
        raise ValidationError(
            {
                "attachments": (
                    f"Можно прикрепить не более {MAX_ATTACHMENTS_PER_REQUEST} файлов."
                )
            }
        )

    return files_list


def _create_attachment(
    *,
    feedback_request: FeedbackRequest,
    file_obj,
) -> FeedbackAttachment:
    """Создаёт вложение обращения."""

    attachment = FeedbackAttachment(
        feedback_request=feedback_request,
        file=file_obj,
        original_name=getattr(file_obj, "name", "") or "",
    )
    attachment.full_clean()
    attachment.save()

    logger.info(
        (
            "Feedback attachment created. "
            "feedback_request_id=%s attachment_id=%s original_name=%s"
        ),
        feedback_request.id,
        attachment.id,
        attachment.original_name,
    )
    return attachment
