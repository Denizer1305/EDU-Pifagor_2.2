from __future__ import annotations

from .actions import (
    CourseArchiveAPIView,
    CourseDuplicateAPIView,
    CoursePublishAPIView,
)
from .crud import (
    CourseDetailAPIView,
    CourseListCreateAPIView,
)
from .public import (
    CoursePublicDetailAPIView,
    CoursePublicListAPIView,
)
from .teachers import (
    CourseTeacherDetailAPIView,
    CourseTeacherListCreateAPIView,
)

__all__ = [
    "CourseArchiveAPIView",
    "CourseDetailAPIView",
    "CourseDuplicateAPIView",
    "CourseListCreateAPIView",
    "CoursePublicDetailAPIView",
    "CoursePublicListAPIView",
    "CoursePublishAPIView",
    "CourseTeacherDetailAPIView",
    "CourseTeacherListCreateAPIView",
]
