from __future__ import annotations

from .academic_year import create_academic_year
from .common import (
    academic_year_counter,
    curriculum_counter,
    education_period_counter,
    student_counter,
    teacher_counter,
    unwrap_factory_result,
)
from .curriculum import create_curriculum, create_curriculum_item
from .education_period import create_education_period
from .group_subject import create_group_subject
from .student_group_enrollment import create_student_group_enrollment
from .teacher_group_subject import create_teacher_group_subject
from .users import create_student_user, create_teacher_user

__all__ = [
    "academic_year_counter",
    "create_academic_year",
    "create_curriculum",
    "create_curriculum_item",
    "create_education_period",
    "create_group_subject",
    "create_student_group_enrollment",
    "create_student_user",
    "create_teacher_group_subject",
    "create_teacher_user",
    "curriculum_counter",
    "education_period_counter",
    "student_counter",
    "teacher_counter",
    "unwrap_factory_result",
]
