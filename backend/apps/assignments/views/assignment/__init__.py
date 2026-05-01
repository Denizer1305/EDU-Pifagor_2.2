from __future__ import annotations

from .actions import (
    AssignmentArchiveAPIView,
    AssignmentDuplicateAPIView,
    AssignmentPublishAPIView,
)
from .detail import AssignmentDetailAPIView
from .list_create import AssignmentListCreateAPIView

__all__ = [
    "AssignmentListCreateAPIView",
    "AssignmentDetailAPIView",
    "AssignmentPublishAPIView",
    "AssignmentArchiveAPIView",
    "AssignmentDuplicateAPIView",
]
