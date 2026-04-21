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
    "RegisterAPIView",
    "LoginAPIView",
    "LogoutAPIView",
    "VerifyEmailAPIView",
    "PasswordResetRequestAPIView",
    "PasswordResetConfirmAPIView",
    "ChangePasswordAPIView",
    "CurrentUserAPIView",
    "UserViewSet",
    "RoleViewSet",
    "UserRoleViewSet",
    "MyProfileAPIView",
    "ProfileViewSet",
    "MyTeacherProfileAPIView",
    "TeacherOnboardingAPIView",
    "TeacherProfileViewSet",
    "TeacherProfileReviewAPIView",
    "MyStudentProfileAPIView",
    "StudentOnboardingAPIView",
    "StudentProfileViewSet",
    "StudentProfileReviewAPIView",
    "MyParentProfileAPIView",
    "ParentProfileViewSet",
    "ParentStudentRequestAPIView",
    "MyParentStudentLinksAPIView",
    "ParentStudentViewSet",
    "ParentStudentReviewAPIView",
]
