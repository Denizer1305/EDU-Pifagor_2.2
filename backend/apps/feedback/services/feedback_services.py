from __future__ import annotations

import logging
from typing import Iterable

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from apps.feedback.models import FeedbackAttachment, FeedbackRequest

logger = logging.getLogger(__name__)


MAX_ATTACHMENTS_PER_REQUEST = 5


def _normalize_text(value: str | None) -> str:
    return (value or "").strip()


def _get_profile(user):
    if not user or not getattr(user, "is_authenticated", False):
        return None
    return getattr(user, "profile", None)


def _get_user_full_name(user) -> str:
    profile = _get_profile(user)
    if profile and getattr(profile, "full_name", ""):
        return profile.full_name

    if user and hasattr(user, "full_name") and user.full_name:
        return user.full_name

    return ""


def _get_user_phone(user) -> str:
    profile = _get_profile(user)
    if profile and getattr(profile, "phone", ""):
        return profile.phone
    return ""


def _get_user_organization_name(user) -> str:
    if not user or not getattr(user, "is_authenticated", False):
        return ""

    teacher_profile = getattr(user, "teacher_profile", None)
    if teacher_profile:
        requested_organization = getattr(teacher_profile, "requested_organization", None)
        if requested_organization is not None:
            return requested_organization.short_name or requested_organization.name

    student_profile = getattr(user, "student_profile", None)
    if student_profile:
        requested_organization = getattr(student_profile, "requested_organization", None)
        if requested_organization is not None:
            return requested_organization.short_name or requested_organization.name

    return ""


def _apply_authenticated_user_defaults(
    *,
    user,
    full_name: str,
    email: str,
    phone: str,
    organization_name: str,
) -> tuple[str, str, str, str]:
    if user and getattr(user, "is_authenticated", False):
        full_name = full_name or _get_user_full_name(user)
        email = email or getattr(user, "email", "")
        phone = phone or _get_user_phone(user)
        organization_name = organization_name or _get_user_organization_name(user)

    return (
        _normalize_text(full_name),
        _normalize_text(email),
        _normalize_text(phone),
        _normalize_text(organization_name),
    )


def _extract_request_meta(request) -> dict[str, str | None]:
    if request is None:
        return {
            "ip_address": None,
            "user_agent": "",
            "referrer": "",
        }

    meta = getattr(request, "META", {}) or {}

    forwarded_for = meta.get("HTTP_X_FORWARDED_FOR", "")
    ip_address = None
    if forwarded_for:
        ip_address = forwarded_for.split(",")[0].strip()
    else:
        ip_address = meta.get("REMOTE_ADDR")

    return {
        "ip_address": ip_address,
        "user_agent": _normalize_text(meta.get("HTTP_USER_AGENT", "")),
        "referrer": _normalize_text(meta.get("HTTP_REFERER", "")),
    }


def _validate_attachments_payload(files: Iterable | None) -> list:
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


def _create_attachment(*, feedback_request: FeedbackRequest, file_obj) -> FeedbackAttachment:
    attachment = FeedbackAttachment(
        feedback_request=feedback_request,
        file=file_obj,
        original_name=getattr(file_obj, "name", "") or "",
    )
    attachment.full_clean()
    attachment.save()

    logger.info(
        "Feedback attachment created. feedback_request_id=%s attachment_id=%s original_name=%s",
        feedback_request.id,
        attachment.id,
        attachment.original_name,
    )
    return attachment


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
    request=None,
) -> FeedbackRequest:
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
        subject = _normalize_text(error_title) or "Сообщение об ошибке"

    feedback_request = FeedbackRequest(
        user=user if user and getattr(user, "is_authenticated", False) else None,
        type=type,
        status=FeedbackRequest.StatusChoices.NEW,
        source=source,
        subject=_normalize_text(subject),
        message=_normalize_text(message),
        full_name=full_name,
        email=email,
        phone=phone,
        organization_name=organization_name,
        is_personal_data_consent=is_personal_data_consent,
        page_url=_normalize_text(page_url),
        frontend_route=_normalize_text(frontend_route),
        error_code=_normalize_text(error_code),
        error_title=_normalize_text(error_title),
        error_details=_normalize_text(error_details),
        client_platform=_normalize_text(client_platform),
        app_version=_normalize_text(app_version),
        ip_address=request_meta["ip_address"],
        user_agent=request_meta["user_agent"],
        referrer=request_meta["referrer"],
    )
    feedback_request.full_clean()
    feedback_request.save()

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
    request=None,
) -> FeedbackRequest:
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
        request=request,
    )


@transaction.atomic
def mark_feedback_in_progress(
    *,
    feedback_request: FeedbackRequest,
    admin_user,
    internal_note: str = "",
) -> FeedbackRequest:
    logger.info(
        "mark_feedback_in_progress started feedback_request_id=%s admin_user_id=%s",
        feedback_request.id,
        getattr(admin_user, "id", None),
    )

    feedback_request.status = FeedbackRequest.StatusChoices.IN_PROGRESS
    if internal_note:
        feedback_request.internal_note = _normalize_text(internal_note)
    feedback_request.full_clean()
    feedback_request.save()

    logger.info(
        "mark_feedback_in_progress completed feedback_request_id=%s",
        feedback_request.id,
    )
    return feedback_request


@transaction.atomic
def resolve_feedback_request(
    *,
    feedback_request: FeedbackRequest,
    admin_user,
    reply_message: str = "",
    internal_note: str = "",
) -> FeedbackRequest:
    logger.info(
        "resolve_feedback_request started feedback_request_id=%s admin_user_id=%s",
        feedback_request.id,
        getattr(admin_user, "id", None),
    )

    feedback_request.status = FeedbackRequest.StatusChoices.RESOLVED
    feedback_request.is_processed = True
    feedback_request.processed_at = timezone.now()
    feedback_request.processed_by = admin_user
    feedback_request.reply_message = _normalize_text(reply_message)
    if internal_note:
        feedback_request.internal_note = _normalize_text(internal_note)

    feedback_request.full_clean()
    feedback_request.save()

    logger.info(
        "resolve_feedback_request completed feedback_request_id=%s",
        feedback_request.id,
    )
    return feedback_request


@transaction.atomic
def reject_feedback_request(
    *,
    feedback_request: FeedbackRequest,
    admin_user,
    reply_message: str = "",
    internal_note: str = "",
) -> FeedbackRequest:
    logger.info(
        "reject_feedback_request started feedback_request_id=%s admin_user_id=%s",
        feedback_request.id,
        getattr(admin_user, "id", None),
    )

    feedback_request.status = FeedbackRequest.StatusChoices.REJECTED
    feedback_request.is_processed = True
    feedback_request.processed_at = timezone.now()
    feedback_request.processed_by = admin_user
    feedback_request.reply_message = _normalize_text(reply_message)
    if internal_note:
        feedback_request.internal_note = _normalize_text(internal_note)

    feedback_request.full_clean()
    feedback_request.save()

    logger.info(
        "reject_feedback_request completed feedback_request_id=%s",
        feedback_request.id,
    )
    return feedback_request


@transaction.atomic
def mark_feedback_as_spam(
    *,
    feedback_request: FeedbackRequest,
    admin_user,
    internal_note: str = "",
) -> FeedbackRequest:
    logger.info(
        "mark_feedback_as_spam started feedback_request_id=%s admin_user_id=%s",
        feedback_request.id,
        getattr(admin_user, "id", None),
    )

    feedback_request.status = FeedbackRequest.StatusChoices.SPAM
    feedback_request.is_spam_suspected = True
    feedback_request.is_processed = True
    feedback_request.processed_at = timezone.now()
    feedback_request.processed_by = admin_user
    if internal_note:
        feedback_request.internal_note = _normalize_text(internal_note)

    feedback_request.full_clean()
    feedback_request.save()

    logger.info(
        "mark_feedback_as_spam completed feedback_request_id=%s",
        feedback_request.id,
    )
    return feedback_request


@transaction.atomic
def archive_feedback_request(
    *,
    feedback_request: FeedbackRequest,
    admin_user,
    internal_note: str = "",
) -> FeedbackRequest:
    logger.info(
        "archive_feedback_request started feedback_request_id=%s admin_user_id=%s",
        feedback_request.id,
        getattr(admin_user, "id", None),
    )

    feedback_request.status = FeedbackRequest.StatusChoices.ARCHIVED
    if internal_note:
        feedback_request.internal_note = _normalize_text(internal_note)

    feedback_request.full_clean()
    feedback_request.save()

    logger.info(
        "archive_feedback_request completed feedback_request_id=%s",
        feedback_request.id,
    )
    return feedback_request
