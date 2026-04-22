from __future__ import annotations

from django.db.models import Q, QuerySet

from apps.feedback.models import FeedbackRequest


def _base_feedback_queryset() -> QuerySet[FeedbackRequest]:
    return FeedbackRequest.objects.select_related(
        "user",
        "user__profile",
        "contact",
        "technical",
        "processing",
        "processing__assigned_to",
        "processing__assigned_to__profile",
        "processing__processed_by",
        "processing__processed_by__profile",
    ).prefetch_related(
        "attachments",
        "status_history",
    )


def get_feedback_requests_queryset(
    *,
    search: str = "",
    status: str = "",
    type: str = "",
    source: str = "",
    is_processed: bool | None = None,
    is_spam_suspected: bool | None = None,
    user_id: int | None = None,
    assigned_to_id: int | None = None,
    processed_by_id: int | None = None,
) -> QuerySet[FeedbackRequest]:
    queryset = _base_feedback_queryset()

    if user_id is not None:
        queryset = queryset.filter(user_id=user_id)

    if assigned_to_id is not None:
        queryset = queryset.filter(processing__assigned_to_id=assigned_to_id)

    if processed_by_id is not None:
        queryset = queryset.filter(processing__processed_by_id=processed_by_id)

    if status:
        queryset = queryset.filter(status=status)

    if type:
        queryset = queryset.filter(type=type)

    if source:
        queryset = queryset.filter(source=source)

    if is_processed is True:
        queryset = queryset.filter(processing__processed_at__isnull=False)
    elif is_processed is False:
        queryset = queryset.filter(processing__processed_at__isnull=True)

    if is_spam_suspected is True:
        queryset = queryset.filter(processing__is_spam_suspected=True)
    elif is_spam_suspected is False:
        queryset = queryset.filter(
            Q(processing__is_spam_suspected=False)
            | Q(processing__is_spam_suspected__isnull=True)
        )

    search = (search or "").strip()
    if search:
        queryset = queryset.filter(
            Q(uid__icontains=search)
            | Q(subject__icontains=search)
            | Q(message__icontains=search)
            | Q(contact__full_name__icontains=search)
            | Q(contact__email__icontains=search)
            | Q(contact__phone__icontains=search)
            | Q(contact__organization_name__icontains=search)
            | Q(technical__page_url__icontains=search)
            | Q(technical__frontend_route__icontains=search)
            | Q(technical__error_code__icontains=search)
            | Q(technical__error_title__icontains=search)
            | Q(technical__error_details__icontains=search)
            | Q(user__email__icontains=search)
            | Q(user__profile__last_name__icontains=search)
            | Q(user__profile__first_name__icontains=search)
            | Q(processing__assigned_to__email__icontains=search)
            | Q(processing__processed_by__email__icontains=search)
            | Q(processing__reply_message__icontains=search)
            | Q(processing__internal_note__icontains=search)
        ).distinct()

    return queryset.order_by("-created_at")


def get_feedback_requests_for_admin_queryset(
    *,
    search: str = "",
    status: str = "",
    type: str = "",
    source: str = "",
    is_processed: bool | None = None,
    is_spam_suspected: bool | None = None,
    assigned_to_id: int | None = None,
    processed_by_id: int | None = None,
) -> QuerySet[FeedbackRequest]:
    return get_feedback_requests_queryset(
        search=search,
        status=status,
        type=type,
        source=source,
        is_processed=is_processed,
        is_spam_suspected=is_spam_suspected,
        assigned_to_id=assigned_to_id,
        processed_by_id=processed_by_id,
    )


def get_my_feedback_requests_queryset(
    *,
    user,
    search: str = "",
    status: str = "",
    type: str = "",
    source: str = "",
) -> QuerySet[FeedbackRequest]:
    if not user or not getattr(user, "is_authenticated", False):
        return FeedbackRequest.objects.none()

    return get_feedback_requests_queryset(
        user_id=user.id,
        search=search,
        status=status,
        type=type,
        source=source,
    )


def get_new_feedback_requests_queryset() -> QuerySet[FeedbackRequest]:
    return _base_feedback_queryset().filter(
        status=FeedbackRequest.StatusChoices.NEW,
    ).order_by("-created_at")


def get_in_progress_feedback_requests_queryset() -> QuerySet[FeedbackRequest]:
    return _base_feedback_queryset().filter(
        status=FeedbackRequest.StatusChoices.IN_PROGRESS,
    ).order_by("-created_at")


def get_waiting_user_feedback_requests_queryset() -> QuerySet[FeedbackRequest]:
    return _base_feedback_queryset().filter(
        status=FeedbackRequest.StatusChoices.WAITING_USER,
    ).order_by("-created_at")


def get_resolved_feedback_requests_queryset() -> QuerySet[FeedbackRequest]:
    return _base_feedback_queryset().filter(
        status=FeedbackRequest.StatusChoices.RESOLVED,
    ).order_by("-created_at")


def get_archived_feedback_requests_queryset() -> QuerySet[FeedbackRequest]:
    return _base_feedback_queryset().filter(
        status=FeedbackRequest.StatusChoices.ARCHIVED,
    ).order_by("-created_at")


def get_spam_feedback_requests_queryset() -> QuerySet[FeedbackRequest]:
    return _base_feedback_queryset().filter(
        Q(status=FeedbackRequest.StatusChoices.SPAM)
        | Q(processing__is_spam_suspected=True)
    ).order_by("-created_at")


def get_feedback_request_by_id(
    *,
    feedback_request_id: int,
) -> FeedbackRequest | None:
    return _base_feedback_queryset().filter(
        id=feedback_request_id,
    ).first()


def get_feedback_request_by_uid(
    *,
    feedback_request_uid,
) -> FeedbackRequest | None:
    return _base_feedback_queryset().filter(
        uid=feedback_request_uid,
    ).first()
