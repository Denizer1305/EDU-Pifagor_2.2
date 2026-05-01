from __future__ import annotations

from apps.feedback.services.feedback_processing_services import (
    archive_feedback_request,
    mark_feedback_as_spam,
    mark_feedback_in_progress,
    reject_feedback_request,
    resolve_feedback_request,
)

from .attachments import (
    _create_attachment,
    _validate_attachments_payload,
)
from .constants import MAX_ATTACHMENTS_PER_REQUEST
from .create import (
    create_contact_feedback_request,
    create_error_feedback_request,
    create_feedback_request,
)
from .related_records import (
    _create_contact,
    _create_processing,
    _create_status_history,
    _create_technical,
)
from .request_meta import _extract_request_meta
from .user_defaults import (
    _apply_authenticated_user_defaults,
    _get_profile,
    _get_user_full_name,
    _get_user_organization_name,
    _get_user_phone,
)

__all__ = [
    "MAX_ATTACHMENTS_PER_REQUEST",
    "_get_profile",
    "_get_user_full_name",
    "_get_user_phone",
    "_get_user_organization_name",
    "_apply_authenticated_user_defaults",
    "_extract_request_meta",
    "_validate_attachments_payload",
    "_create_attachment",
    "_create_contact",
    "_create_technical",
    "_create_processing",
    "_create_status_history",
    "create_feedback_request",
    "create_contact_feedback_request",
    "create_error_feedback_request",
    "mark_feedback_in_progress",
    "resolve_feedback_request",
    "reject_feedback_request",
    "mark_feedback_as_spam",
    "archive_feedback_request",
]
