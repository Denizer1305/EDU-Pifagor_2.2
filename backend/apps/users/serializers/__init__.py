from .auth import (
   LoginSerializer,
   RegisterSerializer,
   ChangePasswordSerializer,
   PasswordResetSerializer,
   PasswordResetConfirmSerializer
)
from .user import (
    UserListSerializer,
    UserDetailSerializer,
    UserUpdateSerializer,
    CurrentUserSerializer,
)
from .profile import (
    Profile,
    ProfileSerializer,
    ProfileDetailSerializer,
    ProfileUpdateSerializer,
)
from .role import (
    RoleSerializer,
    UserRoleSerializer,
)

from .teacher import (
    TeacherProfileListSerializer,
    TeacherProfileDetailSerializer,
    TeacherProfileUpdateSerializer,
)
from .student import (
    StudentProfileDetailSerializer,
    StudentProfileUpdateSerializer,
)
from .parent import (
    ParentStudentSerializer,
    ParentProfileDetailSerializer,
    ParentProfileUpdateSerializer,
)

__all__ = [
    'LoginSerializer',
    'RegisterSerializer',
    'ChangePasswordSerializer',
    'PasswordResetSerializer',
    'PasswordResetConfirmSerializer',

    'UserListSerializer',
    'UserDetailSerializer',
    'UserUpdateSerializer',
    'CurrentUserSerializer',

    'Profile',
    'ProfileSerializer',
    'ProfileDetailSerializer',
    'ProfileUpdateSerializer',

    'RoleSerializer',
    'UserRoleSerializer',

    'TeacherProfileListSerializer',
    'TeacherProfileDetailSerializer',
    'TeacherProfileUpdateSerializer',

    'ParentProfileDetailSerializer',
    'ParentProfileUpdateSerializer',
    'ParentStudentSerializer',

    'StudentProfileDetailSerializer',
    'StudentProfileUpdateSerializer',
]
