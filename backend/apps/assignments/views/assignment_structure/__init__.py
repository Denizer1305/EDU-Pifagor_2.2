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
    "AssignmentAttachmentDetailAPIView",
    "AssignmentAttachmentListCreateAPIView",
    "AssignmentQuestionDetailAPIView",
    "AssignmentQuestionListCreateAPIView",
    "AssignmentQuestionReorderAPIView",
    "AssignmentSectionDetailAPIView",
    "AssignmentSectionListCreateAPIView",
    "AssignmentSectionReorderAPIView",
    "AssignmentVariantDetailAPIView",
    "AssignmentVariantListCreateAPIView",
    "AssignmentVariantReorderAPIView",
]
