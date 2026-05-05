from __future__ import annotations

from .academic_year_admin import AcademicYearAdmin
from .curriculum_admin import CurriculumAdmin, CurriculumItemAdmin
from .curriculum_inline import CurriculumItemInline
from .education_period_admin import EducationPeriodAdmin
from .group_subject_admin import GroupSubjectAdmin
from .student_group_enrollment_admin import StudentGroupEnrollmentAdmin
from .teacher_group_subject_admin import TeacherGroupSubjectAdmin

__all__ = [
    "AcademicYearAdmin",
    "CurriculumAdmin",
    "CurriculumItemAdmin",
    "CurriculumItemInline",
    "EducationPeriodAdmin",
    "GroupSubjectAdmin",
    "StudentGroupEnrollmentAdmin",
    "TeacherGroupSubjectAdmin",
]
