from .academic import (
    AcademicYearDetailView,
    AcademicYearListView,
    EducationPeriodDetailView,
    EducationPeriodListView,
)
from .curriculum import (
    CurriculumDetailView,
    CurriculumItemDetailView,
    CurriculumItemListView,
    CurriculumListView,
)
from .enrollment import (
    StudentGroupEnrollmentDetailView,
    StudentGroupEnrollmentListView,
)
from .load import (
    GroupSubjectDetailView,
    GroupSubjectListView,
    TeacherGroupSubjectDetailView,
    TeacherGroupSubjectListView,
)

__all__ = [
    "AcademicYearDetailView",
    "AcademicYearListView",
    "CurriculumDetailView",
    "CurriculumItemDetailView",
    "CurriculumItemListView",
    "CurriculumListView",
    "EducationPeriodDetailView",
    "EducationPeriodListView",
    "GroupSubjectDetailView",
    "GroupSubjectListView",
    "StudentGroupEnrollmentDetailView",
    "StudentGroupEnrollmentListView",
    "TeacherGroupSubjectDetailView",
    "TeacherGroupSubjectListView",
]
