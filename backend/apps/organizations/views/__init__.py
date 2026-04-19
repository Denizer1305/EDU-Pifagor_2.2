from .group import (
    GroupCuratorDetailView,
    GroupCuratorListView,
    GroupDetailView,
    GroupListView,
    TeacherOrganizationDetailView,
    TeacherOrganizationListView,
    TeacherSubjectDetailView,
    TeacherSubjectListView,
)
from .organization import (
    DepartmentDetailView,
    DepartmentListView,
    OrganizationDetailView,
    OrganizationListView,
    OrganizationTypeDetailView,
    OrganizationTypeListView,
)
from .subject import (
    SubjectCategoryDetailView,
    SubjectCategoryListView,
    SubjectDetailView,
    SubjectListView,
)

__all__ = [
    "OrganizationTypeListView",
    "OrganizationTypeDetailView",
    "OrganizationListView",
    "OrganizationDetailView",
    "DepartmentListView",
    "DepartmentDetailView",
    "SubjectCategoryListView",
    "SubjectCategoryDetailView",
    "SubjectListView",
    "SubjectDetailView",
    "GroupListView",
    "GroupDetailView",
    "GroupCuratorListView",
    "GroupCuratorDetailView",
    "TeacherOrganizationListView",
    "TeacherOrganizationDetailView",
    "TeacherSubjectListView",
    "TeacherSubjectDetailView",
]
