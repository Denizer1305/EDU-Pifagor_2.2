from __future__ import annotations

from .list_detail import (
    CourseDetailSerializer,
    CourseListSerializer,
)
from .mutations import (
    CourseCreateSerializer,
    CourseDuplicateSerializer,
    CourseUpdateSerializer,
)
from .public import (
    CoursePublicDetailSerializer,
    CoursePublicListSerializer,
)
from .short import (
    AcademicYearShortSerializer,
    EducationPeriodShortSerializer,
    GroupSubjectShortSerializer,
    OrganizationShortSerializer,
    SubjectShortSerializer,
    UserShortSerializer,
)
from .teachers import (
    CourseTeacherCreateSerializer,
    CourseTeacherSerializer,
    CourseTeacherUpdateSerializer,
)

__all__ = [
    "UserShortSerializer",
    "OrganizationShortSerializer",
    "SubjectShortSerializer",
    "AcademicYearShortSerializer",
    "EducationPeriodShortSerializer",
    "GroupSubjectShortSerializer",
    "CourseTeacherSerializer",
    "CourseTeacherCreateSerializer",
    "CourseTeacherUpdateSerializer",
    "CourseListSerializer",
    "CourseDetailSerializer",
    "CoursePublicListSerializer",
    "CoursePublicDetailSerializer",
    "CourseCreateSerializer",
    "CourseUpdateSerializer",
    "CourseDuplicateSerializer",
]
