from __future__ import annotations

import logging
from datetime import timedelta

from celery import shared_task
from django.db import transaction
from django.utils import timezone

from apps.feedback.models import FeedbackRequest

logger = logging.getLogger(__name__)


@shared_task
def archive_old_spam_feedback_requests(days: int = 30) -> dict:
    """
    Архивирует старые обращения, помеченные как спам.
    """
    threshold = timezone.now() - timedelta(days=days)

    with transaction.atomic():
        updated_count = FeedbackRequest.objects.filter(
            status=FeedbackRequest.StatusChoices.SPAM,
            created_at__lt=threshold,
        ).exclude(
            status=FeedbackRequest.StatusChoices.ARCHIVED,
        ).update(
            status=FeedbackRequest.StatusChoices.ARCHIVED,
        )

    logger.info(
        "Archived old spam feedback requests. updated_count=%s threshold=%s",
        updated_count,
        threshold.isoformat(),
    )

    return {
        "updated_count": updated_count,
        "threshold": threshold.isoformat(),
    }


@shared_task
def archive_old_resolved_feedback_requests(days: int = 90) -> dict:
    """
    Архивирует старые решённые обращения.
    """
    threshold = timezone.now() - timedelta(days=days)

    with transaction.atomic():
        updated_count = FeedbackRequest.objects.filter(
            status=FeedbackRequest.StatusChoices.RESOLVED,
            processing__processed_at__isnull=False,
            processing__processed_at__lt=threshold,
        ).exclude(
            status=FeedbackRequest.StatusChoices.ARCHIVED,
        ).update(
            status=FeedbackRequest.StatusChoices.ARCHIVED,
        )

    logger.info(
        "Archived old resolved feedback requests. updated_count=%s threshold=%s",
        updated_count,
        threshold.isoformat(),
    )

    return {
        "updated_count": updated_count,
        "threshold": threshold.isoformat(),
    }


@shared_task
def log_feedback_requests_summary() -> dict:
    """
    Логирует сводку по обращениям.
    """
    summary = {
        "total": FeedbackRequest.objects.count(),
        "new": FeedbackRequest.objects.filter(
            status=FeedbackRequest.StatusChoices.NEW
        ).count(),
        "in_progress": FeedbackRequest.objects.filter(
            status=FeedbackRequest.StatusChoices.IN_PROGRESS
        ).count(),
        "resolved": FeedbackRequest.objects.filter(
            status=FeedbackRequest.StatusChoices.RESOLVED
        ).count(),
        "rejected": FeedbackRequest.objects.filter(
            status=FeedbackRequest.StatusChoices.REJECTED
        ).count(),
        "spam": FeedbackRequest.objects.filter(
            status=FeedbackRequest.StatusChoices.SPAM
        ).count(),
        "archived": FeedbackRequest.objects.filter(
            status=FeedbackRequest.StatusChoices.ARCHIVED
        ).count(),
        "from_contacts_page": FeedbackRequest.objects.filter(
            source=FeedbackRequest.SourceChoices.CONTACTS_PAGE
        ).count(),
        "from_error_modal": FeedbackRequest.objects.filter(
            source=FeedbackRequest.SourceChoices.ERROR_MODAL
        ).count(),
        "processed": FeedbackRequest.objects.filter(
            processing__processed_at__isnull=False
        ).count(),
        "spam_suspected": FeedbackRequest.objects.filter(
            processing__is_spam_suspected=True
        ).count(),
        "generated_at": timezone.now().isoformat(),
    }

    logger.info("Feedback requests summary: %s", summary)
    return summary


@shared_task
def mark_stale_feedback_requests_in_progress(days: int = 3) -> dict:
    """
    Помечает старые необработанные новые обращения как требующие внимания.
    Логически ничего не меняет, кроме перевода NEW -> IN_PROGRESS
    для обращений, которые уже долго висят.
    """
    threshold = timezone.now() - timedelta(days=days)

    with transaction.atomic():
        updated_count = FeedbackRequest.objects.filter(
            status=FeedbackRequest.StatusChoices.NEW,
            created_at__lt=threshold,
            processing__processed_at__isnull=True,
        ).update(
            status=FeedbackRequest.StatusChoices.IN_PROGRESS,
        )

    logger.warning(
        "Marked stale feedback requests as in progress. updated_count=%s threshold=%s",
        updated_count,
        threshold.isoformat(),
    )

    return {
        "updated_count": updated_count,
        "threshold": threshold.isoformat(),
    }
