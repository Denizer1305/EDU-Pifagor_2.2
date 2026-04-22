from __future__ import annotations

from django.db.models import Q, QuerySet

from apps.feedback.models import FeedbackRequest


def _base_feedback_queryset() -> QuerySet[FeedbackRequest]:
    return FeedbackRequest.objects.select_related(
        "user",
        "user__profile",
        "processed_by",
        "processed_by__profile",
    ).prefetch_related(
        "attachments",
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
) -> QuerySet[FeedbackRequest]:
    queryset = _base_feedback_queryset()

    if user_id is not None:
        queryset = queryset.filter(user_id=user_id)

    if status:
        queryset = queryset.filter(status=status)

    if type:
        queryset = queryset.filter(type=type)

    if source:
        queryset = queryset.filter(source=source)

    if is_processed is not None:
        queryset = queryset.filter(is_processed=is_processed)

    if is_spam_suspected is not None:
        queryset = queryset.filter(is_spam_suspected=is_spam_suspected)

    search = (search or "").strip()
    if search:
        queryset = queryset.filter(
            Q(subject__icontains=search)
            | Q(message__icontains=search)
            | Q(full_name__icontains=search)
            | Q(email__icontains=search)
            | Q(phone__icontains=search)
            | Q(organization_name__icontains=search)
            | Q(error_code__icontains=search)
            | Q(error_title__icontains=search)
            | Q(error_details__icontains=search)
            | Q(user__email__icontains=search)
            | Q(user__profile__last_name__icontains=search)
            | Q(user__profile__first_name__icontains=search)
            | Q(processed_by__email__icontains=search)
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
) -> QuerySet[FeedbackRequest]:
    return get_feedback_requests_queryset(
        search=search,
        status=status,
        type=type,
        source=source,
        is_processed=is_processed,
        is_spam_suspected=is_spam_suspected,
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


def get_resolved_feedback_requests_queryset() -> QuerySet[FeedbackRequest]:
    return _base_feedback_queryset().filter(
        status=FeedbackRequest.StatusChoices.RESOLVED,
    ).order_by("-created_at")


def get_spam_feedback_requests_queryset() -> QuerySet[FeedbackRequest]:
    return _base_feedback_queryset().filter(
        Q(status=FeedbackRequest.StatusChoices.SPAM)
        | Q(is_spam_suspected=True)
    ).order_by("-created_at")


def get_feedback_request_by_id(
    *,
    feedback_request_id: int,
) -> FeedbackRequest | None:
    return _base_feedback_queryset().filter(
        id=feedback_request_id,
    ).first()
