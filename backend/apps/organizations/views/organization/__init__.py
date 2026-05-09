from __future__ import annotations

from .department import (
    DepartmentDetailView,
    DepartmentListView,
)
from .organization import (
    OrganizationDetailView,
    OrganizationListView,
)
from .organization_type import (
    OrganizationTypeDetailView,
    OrganizationTypeListView,
)
from .teacher_registration_code import (
    OrganizationTeacherRegistrationCodeDisableView,
    OrganizationTeacherRegistrationCodeView,
)

__all__ = [
    "DepartmentDetailView",
    "DepartmentListView",
    "OrganizationDetailView",
    "OrganizationListView",
    "OrganizationTeacherRegistrationCodeDisableView",
    "OrganizationTeacherRegistrationCodeView",
    "OrganizationTypeDetailView",
    "OrganizationTypeListView",
]
