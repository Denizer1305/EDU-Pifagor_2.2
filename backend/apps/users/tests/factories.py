from __future__ import annotations

from django.contrib.auth import get_user_model

from apps.users.models import ParentProfile, Profile, Role, StudentProfile, TeacherProfile, UserRole
from apps.users.constants import ROLE_ADMIN, ROLE_PARENT, ROLE_STUDENT, ROLE_TEACHER

User = get_user_model()


def create_user(
    *,
    email: str = "user@example.com",
    password: str = "TestPass123!",
    reset_email: str | None = None,
    is_active: bool = True,
    is_staff: bool = False,
    is_superuser: bool = False,
):
    user = User.objects.create_user(
        email=email,
        password=password,
        reset_email=reset_email,
        is_active=is_active,
        is_staff=is_staff,
        is_superuser=is_superuser,
    )
    return user


def create_profile(
    *,
    user=None,
    email: str = "profile@example.com",
    first_name: str = "Иван",
    last_name: str = "Иванов",
    patronymic: str = "Иванович",
    phone: str = "+79990000000",
):
    if user is None:
        user = create_user(email=email)

    return Profile.objects.create(
        user=user,
        first_name=first_name,
        last_name=last_name,
        patronymic=patronymic,
        phone=phone,
    )


def create_role(*, code: str, name: str, is_active: bool = True):
    return Role.objects.create(
        code=code,
        name=name,
        is_active=is_active,
    )


def create_system_roles():
    (
        admin_role, _,
    ) = Role.objects.get_or_create(code=ROLE_ADMIN, defaults={"name": "Администратор"})
    (
        teacher_role, _,
    ) = Role.objects.get_or_create(code=ROLE_TEACHER, defaults={"name": "Преподаватель"})
    (
        student_role, _,
    ) = Role.objects.get_or_create(code=ROLE_STUDENT, defaults={"name": "Студент"})
    (
        parent_role, _,
    ) = Role.objects.get_or_create(code=ROLE_PARENT, defaults={"name": "Родитель"})
    return {
        ROLE_ADMIN: admin_role,
        ROLE_TEACHER: teacher_role,
        ROLE_STUDENT: student_role,
        ROLE_PARENT: parent_role,
    }


def assign_role(*, user, code: str):
    roles = create_system_roles()
    role = roles[code]
    return UserRole.objects.create(user=user, role=role)


def create_teacher_user(*, email: str = "teacher@example.com", password: str = "TestPass123!"):
    user = create_user(email=email, password=password)
    create_profile(user=user, email=email, first_name="Мария", last_name="Петрова", patronymic="Игоревна")
    assign_role(user=user, code=ROLE_TEACHER)
    teacher_profile = TeacherProfile.objects.create(
        user=user,
        public_title="Преподаватель математики",
        short_bio="Опытный преподаватель",
        is_public=True,
        show_on_teachers_page=True,
    )
    return (
        user, teacher_profile,
    )


def create_student_user(*, email: str = "student@example.com", password: str = "TestPass123!"):
    user = create_user(email=email, password=password)
    create_profile(user=user, email=email, first_name="Алексей", last_name="Смирнов", patronymic="Олегович")
    assign_role(user=user, code=ROLE_STUDENT)
    student_profile = StudentProfile.objects.create(
        user=user,
        student_code="ST-001",
        admission_year=2025,
    )
    return (
        user, student_profile,
    )


def create_parent_user(*, email: str = "parent@example.com", password: str = "TestPass123!"):
    user = create_user(email=email, password=password)
    create_profile(user=user, email=email, first_name="Елена", last_name="Соколова", patronymic="Павловна")
    assign_role(user=user, code=ROLE_PARENT)
    parent_profile = ParentProfile.objects.create(
        user=user,
        occupation="Инженер",
        work_place="ООО Пример",
    )
    return (
        user, parent_profile,
    )


def create_admin_user(*, email: str = "admin@example.com", password: str = "TestPass123!"):
    user = create_user(
        email=email,
        password=password,
        is_staff=True,
        is_superuser=False,
    )
    create_profile(user=user, email=email, first_name="Админ", last_name="Системный", patronymic="")
    assign_role(user=user, code=ROLE_ADMIN)
    return user
