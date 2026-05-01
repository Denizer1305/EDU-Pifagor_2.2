from __future__ import annotations

from .attachment_admin import FeedbackAttachmentAdmin
from .contact_admin import FeedbackRequestContactAdmin
from .feedback_request_admin import FeedbackRequestAdmin
from .inlines import (
    FeedbackAttachmentInline,
    FeedbackRequestContactInline,
    FeedbackRequestProcessingInline,
    FeedbackRequestTechnicalInline,
    FeedbackStatusHistoryInline,
)
from .processing_admin import FeedbackRequestProcessingAdmin
from .status_history_admin import FeedbackStatusHistoryAdmin
from .technical_admin import FeedbackRequestTechnicalAdmin

__all__ = [
    "FeedbackRequestContactInline",
    "FeedbackRequestTechnicalInline",
    "FeedbackRequestProcessingInline",
    "FeedbackAttachmentInline",
    "FeedbackStatusHistoryInline",
    "FeedbackRequestAdmin",
    "FeedbackRequestContactAdmin",
    "FeedbackRequestTechnicalAdmin",
    "FeedbackRequestProcessingAdmin",
    "FeedbackStatusHistoryAdmin",
    "FeedbackAttachmentAdmin",
]
