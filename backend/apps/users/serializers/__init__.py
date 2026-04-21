from .auth import (
    ChangePasswordSerializer,
    LoginSerializer,
    ParentRegistrationSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetSerializer,
    StudentRegistrationSerializer,
    TeacherRegistrationSerializer,
)
from .parent import (
    ParentProfileSerializer,
    ParentProfileUpdateSerializer,
    ParentStudentRequestSerializer,
    ParentStudentReviewSerializer,
    ParentStudentSerializer,
)
from .profile import (
    ProfileDetailSerializer,
    ProfileSerializer,
    ProfileUpdateSerializer,
)
from .role import RoleSerializer, UserRoleSerializer
from .student import (
    StudentOnboardingSerializer,
    StudentProfileReviewSerializer,
    StudentProfileSerializer,
)
from .teacher import (
    TeacherOnboardingSerializer,
    TeacherProfileReviewSerializer,
    TeacherProfileSerializer,
)
from .user import CurrentUserSerializer

__all__ = [
    "LoginSerializer",
    "StudentRegistrationSerializer",
    "ParentRegistrationSerializer",
    "TeacherRegistrationSerializer",
    "PasswordResetSerializer",
    "PasswordResetConfirmSerializer",
    "ChangePasswordSerializer",
    "ProfileSerializer",
    "ProfileDetailSerializer",
    "ProfileUpdateSerializer",
    "CurrentUserSerializer",
    "StudentProfileSerializer",
    "StudentOnboardingSerializer",
    "StudentProfileReviewSerializer",
    "TeacherProfileSerializer",
    "TeacherOnboardingSerializer",
    "TeacherProfileReviewSerializer",
    "ParentProfileSerializer",
    "ParentProfileUpdateSerializer",
    "ParentStudentSerializer",
    "ParentStudentRequestSerializer",
    "ParentStudentReviewSerializer",
    "RoleSerializer",
    "UserRoleSerializer",
]
