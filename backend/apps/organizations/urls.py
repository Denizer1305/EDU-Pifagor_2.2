from django.urls import path

from apps.organizations.views import (
    DepartmentDetailView,
    DepartmentListView,
    GroupCuratorDetailView,
    GroupCuratorListView,
    GroupDetailView,
    GroupListView,
    OrganizationDetailView,
    OrganizationListView,
    OrganizationTypeDetailView,
    OrganizationTypeListView,
    SubjectCategoryDetailView,
    SubjectCategoryListView,
    SubjectDetailView,
    SubjectListView,
    TeacherOrganizationDetailView,
    TeacherOrganizationListView,
    TeacherSubjectDetailView,
    TeacherSubjectListView,
)

app_name = "organizations"

urlpatterns = [
    path("organization-types/", OrganizationTypeListView.as_view(), name="organization-type-list"),
    path("organization-types/<int:pk>/", OrganizationTypeDetailView.as_view(), name="organization-type-detail"),

    path("organizations/", OrganizationListView.as_view(), name="organization-list"),
    path("organizations/<int:pk>/", OrganizationDetailView.as_view(), name="organization-detail"),

    path("departments/", DepartmentListView.as_view(), name="department-list"),
    path("departments/<int:pk>/", DepartmentDetailView.as_view(), name="department-detail"),

    path("subject-categories/", SubjectCategoryListView.as_view(), name="subject-category-list"),
    path("subject-categories/<int:pk>/", SubjectCategoryDetailView.as_view(), name="subject-category-detail"),

    path("subjects/", SubjectListView.as_view(), name="subject-list"),
    path("subjects/<int:pk>/", SubjectDetailView.as_view(), name="subject-detail"),

    path("groups/", GroupListView.as_view(), name="group-list"),
    path("groups/<int:pk>/", GroupDetailView.as_view(), name="group-detail"),

    path("group-curators/", GroupCuratorListView.as_view(), name="group-curator-list"),
    path("group-curators/<int:pk>/", GroupCuratorDetailView.as_view(), name="group-curator-detail"),

    path("teacher-organizations/", TeacherOrganizationListView.as_view(), name="teacher-organization-list"),
    path("teacher-organizations/<int:pk>/", TeacherOrganizationDetailView.as_view(), name="teacher-organization-detail"),

    path("teacher-subjects/", TeacherSubjectListView.as_view(), name="teacher-subject-list"),
    path("teacher-subjects/<int:pk>/", TeacherSubjectDetailView.as_view(), name="teacher-subject-detail"),
]
