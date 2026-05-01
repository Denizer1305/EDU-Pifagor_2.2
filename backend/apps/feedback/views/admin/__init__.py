from __future__ import annotations

from .detail import FeedbackRequestAdminDetailAPIView
from .list import FeedbackRequestAdminListAPIView
from .permissions import IsAdminOrSuperuser

__all__ = [
    "IsAdminOrSuperuser",
    "FeedbackRequestAdminListAPIView",
    "FeedbackRequestAdminDetailAPIView",
]
