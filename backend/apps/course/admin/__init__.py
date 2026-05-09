from __future__ import annotations

from .assignment_admin import CourseAssignmentAdmin
from .course_admin import CourseAdmin
from .enrollment_admin import CourseEnrollmentAdmin
from .inlines import CourseModuleInline, CourseTeacherInline
from .progress_admin import CourseProgressAdmin, LessonProgressAdmin
from .structure_admin import (
    CourseLessonAdmin,
    CourseMaterialAdmin,
    CourseModuleAdmin,
)
from .teacher_admin import CourseTeacherAdmin

__all__ = [
    "CourseAdmin",
    "CourseAssignmentAdmin",
    "CourseEnrollmentAdmin",
    "CourseLessonAdmin",
    "CourseMaterialAdmin",
    "CourseModuleAdmin",
    "CourseModuleInline",
    "CourseProgressAdmin",
    "CourseTeacherAdmin",
    "CourseTeacherInline",
    "LessonProgressAdmin",
]
