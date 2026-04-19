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
    "AcademicYearListView",
    "AcademicYearDetailView",
    "EducationPeriodListView",
    "EducationPeriodDetailView",
    "StudentGroupEnrollmentListView",
    "StudentGroupEnrollmentDetailView",
    "GroupSubjectListView",
    "GroupSubjectDetailView",
    "TeacherGroupSubjectListView",
    "TeacherGroupSubjectDetailView",
    "CurriculumListView",
    "CurriculumDetailView",
    "CurriculumItemListView",
    "CurriculumItemDetailView",
]
