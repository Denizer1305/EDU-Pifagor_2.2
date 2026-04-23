from __future__ import annotations

from itertools import count

from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone

from apps.feedback.models import (
    FeedbackAttachment,
    FeedbackRequest,
    FeedbackRequestContact,
    FeedbackRequestProcessing,
    FeedbackRequestTechnical,
    FeedbackStatusHistory,
)
from apps.users.tests.factories import create_admin_user, create_profile, create_user


feedback_user_counter = count(1)
feedback_admin_counter = count(1)
feedback_request_counter = count(1)
feedback_attachment_counter = count(1)


def create_feedback_user(
    *,
    email: str | None = None,
    password: str = "TestPass123!",
    first_name: str = "Иван",
    last_name: str = "Иванов",
    patronymic: str = "Иванович",
    phone: str = "+79990000000",
):
    index = next(feedback_user_counter)

    if email is None:
        email = f"feedback_user_{index}@example.com"

    user = create_user(
        email=email,
        password=password,
    )

    create_profile(
        user=user,
        email=email,
        first_name=first_name,
        last_name=f"{last_name}{index}",
        patronymic=patronymic,
        phone=phone,
    )
    return user


def create_feedback_admin_user(*, email: str | None = None):
    index = next(feedback_admin_counter)

    if email is None:
        email = f"feedback_admin_{index}@example.com"

    return create_admin_user(email=email)


def create_uploaded_file(
    *,
    name: str | None = None,
    content: bytes | None = None,
    content_type: str = "application/pdf",
):
    index = next(feedback_attachment_counter)

    if name is None:
        name = f"attachment_{index}.pdf"
    if content is None:
        content = b"test file content"

    return SimpleUploadedFile(
        name=name,
        content=content,
        content_type=content_type,
    )


def create_feedback_request(
    *,
    user=None,
    type: str = FeedbackRequest.TypeChoices.QUESTION,
    status: str = FeedbackRequest.StatusChoices.NEW,
    source: str = FeedbackRequest.SourceChoices.CONTACTS_PAGE,
    subject: str | None = None,
    message: str = "Тестовое сообщение для обратной связи.",
    full_name: str = "",
    email: str = "",
    phone: str = "",
    organization_name: str = "",
    is_personal_data_consent: bool = True,
    personal_data_consent_at=None,
    assigned_to=None,
    assigned_at=None,
    processed_at=None,
    processed_by=None,
    reply_message: str = "",
    internal_note: str = "",
    is_spam_suspected: bool = False,
    page_url: str = "",
    frontend_route: str = "",
    error_code: str = "",
    error_title: str = "",
    error_details: str = "",
    client_platform: str = "",
    app_version: str = "",
    ip_address: str | None = None,
    user_agent: str = "",
    referrer: str = "",
    extra_payload: dict | None = None,
):
    index = next(feedback_request_counter)

    if subject is None:
        subject = f"Обращение {index}"

    if user is not None:
        profile = getattr(user, "profile", None)

        if not full_name and profile is not None and getattr(profile, "full_name", ""):
            full_name = profile.full_name

        if not email:
            email = getattr(user, "email", "")

        if not phone and profile is not None:
            phone = getattr(profile, "phone", "") or ""

    if not email:
        email = f"feedback_request_{index}@example.com"

    if is_personal_data_consent and personal_data_consent_at is None:
        personal_data_consent_at = timezone.now()

    final_statuses = {
        FeedbackRequest.StatusChoices.RESOLVED,
        FeedbackRequest.StatusChoices.REJECTED,
        FeedbackRequest.StatusChoices.SPAM,
        FeedbackRequest.StatusChoices.ARCHIVED,
    }

    if status in final_statuses and processed_at is None:
        processed_at = timezone.now()

    if processed_at is not None and processed_by is None:
        processed_by = create_feedback_admin_user()

    if status == FeedbackRequest.StatusChoices.SPAM and not is_spam_suspected:
        is_spam_suspected = True

    feedback_request = FeedbackRequest(
        user=user,
        type=type,
        status=status,
        source=source,
        subject=subject,
        message=message,
        is_personal_data_consent=is_personal_data_consent,
        personal_data_consent_at=personal_data_consent_at,
    )
    feedback_request.full_clean()
    feedback_request.save()

    contact = FeedbackRequestContact(
        feedback_request=feedback_request,
        full_name=full_name,
        email=email,
        phone=phone,
        organization_name=organization_name,
    )
    contact.full_clean()
    contact.save()

    technical = FeedbackRequestTechnical(
        feedback_request=feedback_request,
        page_url=page_url,
        frontend_route=frontend_route,
        error_code=error_code,
        error_title=error_title,
        error_details=error_details,
        client_platform=client_platform,
        app_version=app_version,
        ip_address=ip_address,
        user_agent=user_agent,
        referrer=referrer,
        extra_payload=extra_payload or {},
    )
    technical.full_clean()
    technical.save()

    processing = FeedbackRequestProcessing(
        feedback_request=feedback_request,
        assigned_to=assigned_to,
        assigned_at=assigned_at,
        processed_by=processed_by,
        processed_at=processed_at,
        reply_message=reply_message,
        internal_note=internal_note,
        is_spam_suspected=is_spam_suspected,
    )
    processing.full_clean()
    processing.save()

    history = FeedbackStatusHistory(
        feedback_request=feedback_request,
        from_status="",
        to_status=status,
        changed_by=processed_by if processed_by else None,
        comment="Тестовое создание обращения.",
    )
    history.full_clean()
    history.save()

    return feedback_request


def create_feedback_attachment(
    *,
    feedback_request=None,
    file=None,
):
    if feedback_request is None:
        feedback_request = create_feedback_request()

    if file is None:
        file = create_uploaded_file()

    attachment = FeedbackAttachment(
        feedback_request=feedback_request,
        file=file,
        original_name=getattr(file, "name", ""),
    )
    attachment.full_clean()
    attachment.save()
    return attachment
