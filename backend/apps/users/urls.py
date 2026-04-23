from __future__ import annotations

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.users.views import (
    ChangePasswordAPIView,
    CurrentUserAPIView,
    LoginAPIView,
    LogoutAPIView,
    MyParentProfileAPIView,
    MyParentStudentLinksAPIView,
    MyProfileAPIView,
    MyStudentProfileAPIView,
    MyTeacherProfileAPIView,
    ParentProfileViewSet,
    ParentStudentRequestAPIView,
    ParentStudentReviewAPIView,
    ParentStudentViewSet,
    PasswordResetConfirmAPIView,
    PasswordResetRequestAPIView,
    ProfileViewSet,
    RegisterAPIView,
    RoleViewSet,
    StudentOnboardingAPIView,
    StudentProfileReviewAPIView,
    StudentProfileViewSet,
    TeacherOnboardingAPIView,
    TeacherProfileReviewAPIView,
    TeacherProfileViewSet,
    UserRoleViewSet,
    UserViewSet,
    VerifyEmailAPIView,
)

app_name = "users"

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")
router.register(r"roles", RoleViewSet, basename="role")
router.register(r"user-roles", UserRoleViewSet, basename="user-role")
router.register(r"profiles", ProfileViewSet, basename="profile")
router.register(r"teacher-profiles", TeacherProfileViewSet, basename="teacher-profile")
router.register(r"student-profiles", StudentProfileViewSet, basename="student-profile")
router.register(r"parent-profiles", ParentProfileViewSet, basename="parent-profile")
router.register(r"parent-student-links", ParentStudentViewSet, basename="parent-student-link")

urlpatterns = [
    path("auth/register/", RegisterAPIView.as_view(), name="register"),
    path("auth/login/", LoginAPIView.as_view(), name="login"),
    path("auth/logout/", LogoutAPIView.as_view(), name="logout"),
    path("auth/verify-email/", VerifyEmailAPIView.as_view(), name="verify-email"),
    path("auth/password-reset/", PasswordResetRequestAPIView.as_view(), name="password-reset"),
    path(
        "auth/password-reset/confirm/",
        PasswordResetConfirmAPIView.as_view(),
        name="password-reset-confirm",
    ),
    path("auth/change-password/", ChangePasswordAPIView.as_view(), name="change-password"),

    path("me/", CurrentUserAPIView.as_view(), name="current-user"),
    path("me/profile/", MyProfileAPIView.as_view(), name="my-profile"),

    path("me/student-profile/", MyStudentProfileAPIView.as_view(), name="my-student-profile"),
    path(
        "me/student-profile/onboarding/",
        StudentOnboardingAPIView.as_view(),
        name="student-onboarding",
    ),

    path("me/teacher-profile/", MyTeacherProfileAPIView.as_view(), name="my-teacher-profile"),
    path(
        "me/teacher-profile/onboarding/",
        TeacherOnboardingAPIView.as_view(),
        name="teacher-onboarding",
    ),

    path("me/parent-profile/", MyParentProfileAPIView.as_view(), name="my-parent-profile"),
    path(
        "me/parent-student-links/",
        MyParentStudentLinksAPIView.as_view(),
        name="my-parent-student-links",
    ),
    path(
        "me/parent-student-links/request/",
        ParentStudentRequestAPIView.as_view(),
        name="parent-student-link-request",
    ),

    path(
        "student-profiles/<int:pk>/review/",
        StudentProfileReviewAPIView.as_view(),
        name="student-profile-review",
    ),
    path(
        "teacher-profiles/<int:pk>/review/",
        TeacherProfileReviewAPIView.as_view(),
        name="teacher-profile-review",
    ),
    path(
        "parent-student-links/<int:pk>/review/",
        ParentStudentReviewAPIView.as_view(),
        name="parent-student-link-review",
    ),

    path("", include(router.urls)),
]
