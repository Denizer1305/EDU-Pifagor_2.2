from __future__ import annotations

from apps.feedback.models import (
    FeedbackRequest,
    FeedbackRequestContact,
    FeedbackRequestProcessing,
    FeedbackRequestTechnical,
    FeedbackStatusHistory,
)
from apps.feedback.models.base import normalize_text


def _create_contact(
    *,
    feedback_request: FeedbackRequest,
    full_name: str,
    email: str,
    phone: str,
    organization_name: str,
) -> FeedbackRequestContact:
    """Создаёт контактные данные обращения."""

    contact = FeedbackRequestContact(
        feedback_request=feedback_request,
        full_name=full_name,
        email=email,
        phone=phone,
        organization_name=organization_name,
    )
    contact.full_clean()
    contact.save()
    return contact


def _create_technical(
    *,
    feedback_request: FeedbackRequest,
    page_url: str,
    frontend_route: str,
    error_code: str,
    error_title: str,
    error_details: str,
    client_platform: str,
    app_version: str,
    ip_address,
    user_agent: str,
    referrer: str,
    extra_payload: dict | None = None,
) -> FeedbackRequestTechnical:
    """Создаёт технические данные обращения."""

    technical = FeedbackRequestTechnical(
        feedback_request=feedback_request,
        page_url=normalize_text(page_url),
        frontend_route=normalize_text(frontend_route),
        error_code=normalize_text(error_code),
        error_title=normalize_text(error_title),
        error_details=normalize_text(error_details),
        client_platform=normalize_text(client_platform),
        app_version=normalize_text(app_version),
        ip_address=ip_address,
        user_agent=normalize_text(user_agent),
        referrer=normalize_text(referrer),
        extra_payload=extra_payload or {},
    )
    technical.full_clean()
    technical.save()
    return technical


def _create_processing(
    *,
    feedback_request: FeedbackRequest,
) -> FeedbackRequestProcessing:
    """Создаёт первичную запись обработки обращения."""

    processing = FeedbackRequestProcessing(
        feedback_request=feedback_request,
    )
    processing.full_clean()
    processing.save()
    return processing


def _create_status_history(
    *,
    feedback_request: FeedbackRequest,
    from_status: str,
    to_status: str,
    changed_by=None,
    comment: str = "",
) -> FeedbackStatusHistory:
    """Создаёт запись истории статуса обращения."""

    history = FeedbackStatusHistory(
        feedback_request=feedback_request,
        from_status=normalize_text(from_status),
        to_status=to_status,
        changed_by=changed_by,
        comment=normalize_text(comment),
    )
    history.full_clean()
    history.save()
    return history
