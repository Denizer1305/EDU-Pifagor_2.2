from __future__ import annotations

from .attachments import (
    AssignmentAttachmentDetailAPIView,
    AssignmentAttachmentListCreateAPIView,
)
from .questions import (
    AssignmentQuestionDetailAPIView,
    AssignmentQuestionListCreateAPIView,
    AssignmentQuestionReorderAPIView,
)
from .sections import (
    AssignmentSectionDetailAPIView,
    AssignmentSectionListCreateAPIView,
    AssignmentSectionReorderAPIView,
)
from .variants import (
    AssignmentVariantDetailAPIView,
    AssignmentVariantListCreateAPIView,
    AssignmentVariantReorderAPIView,
)

__all__ = [
    "AssignmentVariantListCreateAPIView",
    "AssignmentVariantDetailAPIView",
    "AssignmentVariantReorderAPIView",
    "AssignmentSectionListCreateAPIView",
    "AssignmentSectionDetailAPIView",
    "AssignmentSectionReorderAPIView",
    "AssignmentQuestionListCreateAPIView",
    "AssignmentQuestionDetailAPIView",
    "AssignmentQuestionReorderAPIView",
    "AssignmentAttachmentListCreateAPIView",
    "AssignmentAttachmentDetailAPIView",
]
