from __future__ import annotations

from .lessons import (
    CourseLessonDetailAPIView,
    CourseLessonListCreateAPIView,
    CourseLessonMoveAPIView,
    CourseLessonReorderAPIView,
)
from .materials import (
    CourseMaterialDetailAPIView,
    CourseMaterialListCreateAPIView,
)
from .modules import (
    CourseModuleDetailAPIView,
    CourseModuleListCreateAPIView,
    CourseModuleReorderAPIView,
)

__all__ = [
    "CourseLessonDetailAPIView",
    "CourseLessonListCreateAPIView",
    "CourseLessonMoveAPIView",
    "CourseLessonReorderAPIView",
    "CourseMaterialDetailAPIView",
    "CourseMaterialListCreateAPIView",
    "CourseModuleDetailAPIView",
    "CourseModuleListCreateAPIView",
    "CourseModuleReorderAPIView",
]
