from __future__ import annotations

import logging
from typing import Iterable

from django.db import transaction

from apps.feedback.models import FeedbackRequest
from apps.feedback.models.base import normalize_text
from apps.feedback.services.feedback_services.attachments import (
    _create_attachment,
    _validate_attachments_payload,
)
from apps.feedback.services.feedback_services.related_records import (
    _create_contact,
    _create_processing,
    _create_status_history,
    _create_technical,
)
from apps.feedback.services.feedback_services.request_meta import _extract_request_meta
from apps.feedback.services.feedback_services.user_defaults import (
    _apply_authenticated_user_defaults,
)

logger = logging.getLogger(__name__)


@transaction.atomic
def create_feedback_request(
    *,
    user=None,
    type: str = FeedbackRequest.TypeChoices.QUESTION,
    source: str = FeedbackRequest.SourceChoices.CONTACTS_PAGE,
    subject: str = "",
    message: str,
    full_name: str = "",
    email: str = "",
    phone: str = "",
    organization_name: str = "",
    is_personal_data_consent: bool,
    files: Iterable | None = None,
    page_url: str = "",
    frontend_route: str = "",
    error_code: str = "",
    error_title: str = "",
    error_details: str = "",
    client_platform: str = "",
    app_version: str = "",
    extra_payload: dict | None = None,
    request=None,
) -> FeedbackRequest:
    """Создаёт обращение обратной связи со всеми связанными данными."""

    logger.info(
        "create_feedback_request started source=%s type=%s authenticated=%s",
        source,
        type,
        bool(user and getattr(user, "is_authenticated", False)),
    )

    files_list = _validate_attachments_payload(files)

    full_name, email, phone, organization_name = _apply_authenticated_user_defaults(
        user=user,
        full_name=full_name,
        email=email,
        phone=phone,
        organization_name=organization_name,
    )

    request_meta = _extract_request_meta(request)

    if source == FeedbackRequest.SourceChoices.ERROR_MODAL and not type:
        type = FeedbackRequest.TypeChoices.BUG

    if source == FeedbackRequest.SourceChoices.ERROR_MODAL and not subject:
        subject = normalize_text(error_title) or "Сообщение об ошибке"

    feedback_request = FeedbackRequest(
        user=user if user and getattr(user, "is_authenticated", False) else None,
        type=type,
        status=FeedbackRequest.StatusChoices.NEW,
        source=source,
        subject=normalize_text(subject),
        message=normalize_text(message),
        is_personal_data_consent=is_personal_data_consent,
    )
    feedback_request.full_clean()
    feedback_request.save()

    _create_contact(
        feedback_request=feedback_request,
        full_name=full_name,
        email=email,
        phone=phone,
        organization_name=organization_name,
    )

    _create_technical(
        feedback_request=feedback_request,
        page_url=page_url,
        frontend_route=frontend_route,
        error_code=error_code,
        error_title=error_title,
        error_details=error_details,
        client_platform=client_platform,
        app_version=app_version,
        ip_address=request_meta["ip_address"],
        user_agent=request_meta["user_agent"],
        referrer=request_meta["referrer"],
        extra_payload=extra_payload,
    )

    _create_processing(
        feedback_request=feedback_request,
    )

    _create_status_history(
        feedback_request=feedback_request,
        from_status="",
        to_status=FeedbackRequest.StatusChoices.NEW,
        changed_by=user if user and getattr(user, "is_authenticated", False) else None,
        comment="Обращение создано.",
    )

    for file_obj in files_list:
        _create_attachment(
            feedback_request=feedback_request,
            file_obj=file_obj,
        )

    logger.info(
        "create_feedback_request completed id=%s source=%s attachments_count=%s",
        feedback_request.id,
        feedback_request.source,
        len(files_list),
    )
    return feedback_request


def create_contact_feedback_request(
    *,
    user=None,
    subject: str = "",
    message: str,
    full_name: str = "",
    email: str = "",
    phone: str = "",
    organization_name: str = "",
    type: str = FeedbackRequest.TypeChoices.QUESTION,
    is_personal_data_consent: bool,
    files: Iterable | None = None,
    request=None,
) -> FeedbackRequest:
    """Создаёт обращение с формы контактов."""

    return create_feedback_request(
        user=user,
        type=type,
        source=FeedbackRequest.SourceChoices.CONTACTS_PAGE,
        subject=subject,
        message=message,
        full_name=full_name,
        email=email,
        phone=phone,
        organization_name=organization_name,
        is_personal_data_consent=is_personal_data_consent,
        files=files,
        request=request,
    )


def create_error_feedback_request(
    *,
    user=None,
    subject: str = "",
    message: str,
    full_name: str = "",
    email: str = "",
    phone: str = "",
    organization_name: str = "",
    type: str = FeedbackRequest.TypeChoices.BUG,
    is_personal_data_consent: bool,
    files: Iterable | None = None,
    page_url: str = "",
    frontend_route: str = "",
    error_code: str = "",
    error_title: str = "",
    error_details: str = "",
    client_platform: str = "",
    app_version: str = "",
    extra_payload: dict | None = None,
    request=None,
) -> FeedbackRequest:
    """Создаёт обращение из модального окна ошибки."""

    return create_feedback_request(
        user=user,
        type=type or FeedbackRequest.TypeChoices.BUG,
        source=FeedbackRequest.SourceChoices.ERROR_MODAL,
        subject=subject,
        message=message,
        full_name=full_name,
        email=email,
        phone=phone,
        organization_name=organization_name,
        is_personal_data_consent=is_personal_data_consent,
        files=files,
        page_url=page_url,
        frontend_route=frontend_route,
        error_code=error_code,
        error_title=error_title,
        error_details=error_details,
        client_platform=client_platform,
        app_version=app_version,
        extra_payload=extra_payload,
        request=request,
    )
