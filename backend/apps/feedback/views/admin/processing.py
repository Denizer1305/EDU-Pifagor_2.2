from __future__ import annotations

from django.utils import timezone

from apps.feedback.models import FeedbackRequest, FeedbackRequestProcessing
from apps.feedback.services.feedback_services import (
    archive_feedback_request,
    mark_feedback_as_spam,
    mark_feedback_in_progress,
    reject_feedback_request,
    resolve_feedback_request,
)


def get_or_create_processing(
    feedback_request: FeedbackRequest,
) -> FeedbackRequestProcessing:
    """Возвращает processing-запись обращения или создаёт её."""

    processing, _ = FeedbackRequestProcessing.objects.get_or_create(
        feedback_request=feedback_request,
    )
    return processing


def apply_status_action(
    *,
    feedback_request: FeedbackRequest,
    admin_user,
    status_value: str | None,
    reply_message: str = "",
    internal_note: str = "",
) -> FeedbackRequest | None:
    """Выполняет статусное действие над обращением.

    Возвращает обновлённое обращение, если статусное действие было выполнено.
    Если статус не передан или не является действием, возвращает None.
    """

    if status_value == feedback_request.StatusChoices.IN_PROGRESS:
        return mark_feedback_in_progress(
            feedback_request=feedback_request,
            admin_user=admin_user,
            internal_note=internal_note,
        )

    if status_value == feedback_request.StatusChoices.RESOLVED:
        return resolve_feedback_request(
            feedback_request=feedback_request,
            admin_user=admin_user,
            reply_message=reply_message,
            internal_note=internal_note,
        )

    if status_value == feedback_request.StatusChoices.REJECTED:
        return reject_feedback_request(
            feedback_request=feedback_request,
            admin_user=admin_user,
            reply_message=reply_message,
            internal_note=internal_note,
        )

    if status_value == feedback_request.StatusChoices.SPAM:
        return mark_feedback_as_spam(
            feedback_request=feedback_request,
            admin_user=admin_user,
            internal_note=internal_note,
        )

    if status_value == feedback_request.StatusChoices.ARCHIVED:
        return archive_feedback_request(
            feedback_request=feedback_request,
            admin_user=admin_user,
            internal_note=internal_note,
        )

    return None


def update_processing_fields(
    *,
    feedback_request: FeedbackRequest,
    admin_user,
    validated_data: dict,
) -> FeedbackRequestProcessing:
    """Обновляет processing-поля без смены статуса обращения."""

    processing = get_or_create_processing(feedback_request)
    update_fields: list[str] = []

    if "reply_message" in validated_data:
        processing.reply_message = validated_data.get("reply_message", "")
        update_fields.append("reply_message")

    if "internal_note" in validated_data:
        processing.internal_note = validated_data.get("internal_note", "")
        update_fields.append("internal_note")

    if "is_spam_suspected" in validated_data:
        processing.is_spam_suspected = validated_data["is_spam_suspected"]
        update_fields.append("is_spam_suspected")

    if "is_processed" in validated_data:
        if validated_data["is_processed"]:
            if not processing.processed_at:
                processing.processed_at = timezone.now()
                update_fields.append("processed_at")

            if not processing.processed_by_id:
                processing.processed_by = admin_user
                update_fields.append("processed_by")
        else:
            processing.processed_at = None
            processing.processed_by = None
            update_fields.extend(["processed_at", "processed_by"])

    processing.full_clean()

    if update_fields:
        if "updated_at" not in update_fields:
            update_fields.append("updated_at")

        processing.save(update_fields=update_fields)

    return processing
