from .auth import (
    ChangePasswordAPIView,
    LoginAPIView,
    LogoutAPIView,
    PasswordResetConfirmAPIView,
    PasswordResetRequestAPIView,
    RegisterAPIView,
    VerifyEmailAPIView,
)
from .parent import (
    MyParentProfileAPIView,
    MyParentStudentLinksAPIView,
    ParentProfileViewSet,
    ParentStudentRequestAPIView,
    ParentStudentReviewAPIView,
    ParentStudentViewSet,
)
from .profile import MyProfileAPIView, ProfileViewSet
from .role import RoleViewSet, UserRoleViewSet
from .student import (
    MyStudentProfileAPIView,
    StudentOnboardingAPIView,
    StudentProfileReviewAPIView,
    StudentProfileViewSet,
)
from .teacher import (
    MyTeacherProfileAPIView,
    TeacherOnboardingAPIView,
    TeacherProfileReviewAPIView,
    TeacherProfileViewSet,
)
from .user import CurrentUserAPIView, UserViewSet

__all__ = [
    "ChangePasswordAPIView",
    "CurrentUserAPIView",
    "LoginAPIView",
    "LogoutAPIView",
    "MyParentProfileAPIView",
    "MyParentStudentLinksAPIView",
    "MyProfileAPIView",
    "MyStudentProfileAPIView",
    "MyTeacherProfileAPIView",
    "ParentProfileViewSet",
    "ParentStudentRequestAPIView",
    "ParentStudentReviewAPIView",
    "ParentStudentViewSet",
    "PasswordResetConfirmAPIView",
    "PasswordResetRequestAPIView",
    "ProfileViewSet",
    "RegisterAPIView",
    "RoleViewSet",
    "StudentOnboardingAPIView",
    "StudentProfileReviewAPIView",
    "StudentProfileViewSet",
    "TeacherOnboardingAPIView",
    "TeacherProfileReviewAPIView",
    "TeacherProfileViewSet",
    "UserRoleViewSet",
    "UserViewSet",
    "VerifyEmailAPIView",
]
