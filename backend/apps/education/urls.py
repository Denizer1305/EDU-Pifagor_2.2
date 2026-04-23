from django.urls import path

from apps.education.views import (
    AcademicYearDetailView,
    AcademicYearListView,
    CurriculumDetailView,
    CurriculumItemDetailView,
    CurriculumItemListView,
    CurriculumListView,
    EducationPeriodDetailView,
    EducationPeriodListView,
    GroupSubjectDetailView,
    GroupSubjectListView,
    StudentGroupEnrollmentDetailView,
    StudentGroupEnrollmentListView,
    TeacherGroupSubjectDetailView,
    TeacherGroupSubjectListView,
)

app_name = "education"

urlpatterns = [
    path(
        "academic-years/",
        AcademicYearListView.as_view(),
        name="academic-year-list",
    ),
    path(
        "academic-years/<int:pk>/",
        AcademicYearDetailView.as_view(),
        name="academic-year-detail",
    ),

    path(
        "periods/",
        EducationPeriodListView.as_view(),
        name="education-period-list",
    ),
    path(
        "periods/<int:pk>/",
        EducationPeriodDetailView.as_view(),
        name="education-period-detail",
    ),

    path(
        "enrollments/",
        StudentGroupEnrollmentListView.as_view(),
        name="student-group-enrollment-list",
    ),
    path(
        "enrollments/<int:pk>/",
        StudentGroupEnrollmentDetailView.as_view(),
        name="student-group-enrollment-detail",
    ),

    path(
        "group-subjects/",
        GroupSubjectListView.as_view(),
        name="group-subject-list",
    ),
    path(
        "group-subjects/<int:pk>/",
        GroupSubjectDetailView.as_view(),
        name="group-subject-detail",
    ),

    path(
        "teacher-group-subjects/",
        TeacherGroupSubjectListView.as_view(),
        name="teacher-group-subject-list",
    ),
    path(
        "teacher-group-subjects/<int:pk>/",
        TeacherGroupSubjectDetailView.as_view(),
        name="teacher-group-subject-detail",
    ),

    path(
        "curricula/",
        CurriculumListView.as_view(),
        name="curriculum-list",
    ),
    path(
        "curricula/<int:pk>/",
        CurriculumDetailView.as_view(),
        name="curriculum-detail",
    ),

    path(
        "curriculum-items/",
        CurriculumItemListView.as_view(),
        name="curriculum-item-list",
    ),
    path(
        "curriculum-items/<int:pk>/",
        CurriculumItemDetailView.as_view(),
        name="curriculum-item-detail",
    ),
]
