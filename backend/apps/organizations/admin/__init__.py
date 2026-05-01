from __future__ import annotations

from .actions import (
    clear_group_join_code,
    clear_teacher_registration_code,
    disable_group_join_code,
    disable_teacher_registration_code,
)
from .department_admin import DepartmentAdmin
from .group_admin import GroupAdmin
from .group_curator_admin import GroupCuratorAdmin
from .organization_admin import OrganizationAdmin
from .organization_type_admin import OrganizationTypeAdmin
from .subject_admin import SubjectAdmin
from .subject_category_admin import SubjectCategoryAdmin
from .teacher_organization_admin import TeacherOrganizationAdmin
from .teacher_subject_admin import TeacherSubjectAdmin

__all__ = [
    "disable_teacher_registration_code",
    "clear_teacher_registration_code",
    "disable_group_join_code",
    "clear_group_join_code",
    "OrganizationTypeAdmin",
    "OrganizationAdmin",
    "DepartmentAdmin",
    "GroupAdmin",
    "GroupCuratorAdmin",
    "SubjectCategoryAdmin",
    "SubjectAdmin",
    "TeacherOrganizationAdmin",
    "TeacherSubjectAdmin",
]
