from __future__ import annotations

from .attachments import (
    AssignmentAttachmentSerializer,
    AssignmentAttachmentWriteSerializer,
)
from .questions import (
    AssignmentQuestionSerializer,
    AssignmentQuestionWriteSerializer,
)
from .sections import (
    AssignmentSectionSerializer,
    AssignmentSectionWriteSerializer,
)
from .variants import (
    AssignmentVariantSerializer,
    AssignmentVariantWriteSerializer,
)

__all__ = [
    "AssignmentAttachmentSerializer",
    "AssignmentAttachmentWriteSerializer",
    "AssignmentQuestionSerializer",
    "AssignmentQuestionWriteSerializer",
    "AssignmentSectionSerializer",
    "AssignmentSectionWriteSerializer",
    "AssignmentVariantSerializer",
    "AssignmentVariantWriteSerializer",
]
