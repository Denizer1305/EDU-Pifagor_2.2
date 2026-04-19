from django.utils.translation import gettext_lazy as _

ROLE_ADMIN = 'admin'
ROLE_TEACHER = 'teacher'
ROLE_STUDENT = 'student'
ROLE_PARENT = 'parent'

SYSTEM_ROLE_CODES = (
    ROLE_ADMIN, ROLE_TEACHER,
    ROLE_STUDENT, ROLE_PARENT,
)

SYSTEM_ROLE_NAMES = {
    ROLE_ADMIN: _('Администратор'),
    ROLE_TEACHER: _('Преподаватель'),
    ROLE_STUDENT: _('Студент'),
    ROLE_PARENT: _('Родитель'),
}

MAX_NAME_LENGTH = 255
MAX_PHONE_NUMBER = 32
MAX_STUDENT_CODE_LENGTH = 64
