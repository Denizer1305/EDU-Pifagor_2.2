from __future__ import annotations

from .curator import (
    GroupCuratorDetailView,
    GroupCuratorListView,
)
from .group import (
    GroupDetailView,
    GroupListView,
)
from .join_code import GroupJoinCodeView
from .teacher_organization import (
    TeacherOrganizationDetailView,
    TeacherOrganizationListView,
    TeacherOrganizationSetPrimaryView,
)
from .teacher_subject import (
    TeacherSubjectDetailView,
    TeacherSubjectListView,
)

__all__ = [
    "GroupListView",
    "GroupDetailView",
    "GroupJoinCodeView",
    "GroupCuratorListView",
    "GroupCuratorDetailView",
    "TeacherOrganizationListView",
    "TeacherOrganizationDetailView",
    "TeacherOrganizationSetPrimaryView",
    "TeacherSubjectListView",
    "TeacherSubjectDetailView",
]
