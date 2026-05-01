from __future__ import annotations

from .parent_profile_admin import ParentProfileAdmin
from .parent_student_admin import ParentStudentAdmin
from .profile_admin import ProfileAdmin
from .role_admin import RoleAdmin
from .student_profile_admin import StudentProfileAdmin
from .teacher_profile_admin import TeacherProfileAdmin
from .user_admin import UserAdmin
from .user_role_admin import UserRoleAdmin

__all__ = [
    "UserAdmin",
    "ProfileAdmin",
    "RoleAdmin",
    "UserRoleAdmin",
    "TeacherProfileAdmin",
    "StudentProfileAdmin",
    "ParentProfileAdmin",
    "ParentStudentAdmin",
]
