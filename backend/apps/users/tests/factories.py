from __future__ import annotations

from django.contrib.auth import get_user_model

from apps.users.constants import ROLE_ADMIN, ROLE_PARENT, ROLE_STUDENT, ROLE_TEACHER
from apps.users.models import (
    Role,
    UserRole,
)
from apps.users.services.profile_services import (
    ensure_role_profile,
    get_or_create_base_profile,
)

User = get_user_model()


def create_user(
    *,
    email: str = "user@example.com",
    password: str = "TestPass123!",
    reset_email: str | None = None,
    registration_type: str = "student",
    is_active: bool = True,
    is_staff: bool = False,
    is_superuser: bool = False,
):
    return User.objects.create_user(
        email=email,
        password=password,
        reset_email=reset_email,
        registration_type=registration_type,
        is_active=is_active,
        is_staff=is_staff,
        is_superuser=is_superuser,
    )


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

    profile = get_or_create_base_profile(user)
    profile.first_name = first_name
    profile.last_name = last_name
    profile.patronymic = patronymic
    profile.phone = phone
    profile.full_clean()
    profile.save()
    return profile


def create_role(*, code: str, name: str, is_active: bool = True):
    return Role.objects.create(
        code=code,
        name=name,
        is_active=is_active,
    )


def create_system_roles():
    admin_role, _ = Role.objects.get_or_create(
        code=ROLE_ADMIN,
        defaults={"name": "Администратор", "is_active": True},
    )
    teacher_role, _ = Role.objects.get_or_create(
        code=ROLE_TEACHER,
        defaults={"name": "Преподаватель", "is_active": True},
    )
    student_role, _ = Role.objects.get_or_create(
        code=ROLE_STUDENT,
        defaults={"name": "Студент", "is_active": True},
    )
    parent_role, _ = Role.objects.get_or_create(
        code=ROLE_PARENT,
        defaults={"name": "Родитель", "is_active": True},
    )
    return {
        ROLE_ADMIN: admin_role,
        ROLE_TEACHER: teacher_role,
        ROLE_STUDENT: student_role,
        ROLE_PARENT: parent_role,
    }


def assign_role(*, user, code: str):
    role = create_system_roles()[code]
    return UserRole.objects.get_or_create(user=user, role=role)[0]


def create_teacher_user(
    *,
    email: str = "teacher@example.com",
    password: str = "TestPass123!",
):
    user = create_user(
        email=email,
        password=password,
        registration_type="teacher",
    )
    create_profile(
        user=user,
        email=email,
        first_name="Мария",
        last_name="Петрова",
        patronymic="Игоревна",
    )
    assign_role(user=user, code=ROLE_TEACHER)
    teacher_profile = ensure_role_profile(user)

    if hasattr(teacher_profile, "position"):
        teacher_profile.position = "Преподаватель математики"
    if hasattr(teacher_profile, "employee_code"):
        teacher_profile.employee_code = "EMP-001"
    if hasattr(teacher_profile, "verification_status"):
        teacher_profile.verification_status = "pending"

    teacher_profile.full_clean()
    teacher_profile.save()

    return user, teacher_profile


def create_student_user(
    *,
    email: str = "student@example.com",
    password: str = "TestPass123!",
):
    user = create_user(
        email=email,
        password=password,
        registration_type="student",
    )
    create_profile(
        user=user,
        email=email,
        first_name="Алексей",
        last_name="Смирнов",
        patronymic="Олегович",
    )
    assign_role(user=user, code=ROLE_STUDENT)
    student_profile = ensure_role_profile(user)

    if hasattr(student_profile, "student_code"):
        student_profile.student_code = "ST-001"

    student_profile.full_clean()
    student_profile.save()

    return user, student_profile


def create_parent_user(
    *,
    email: str = "parent@example.com",
    password: str = "TestPass123!",
):
    user = create_user(
        email=email,
        password=password,
        registration_type="parent",
    )
    create_profile(
        user=user,
        email=email,
        first_name="Елена",
        last_name="Соколова",
        patronymic="Павловна",
    )
    assign_role(user=user, code=ROLE_PARENT)
    parent_profile = ensure_role_profile(user)

    if hasattr(parent_profile, "work_place"):
        parent_profile.work_place = "ООО Пример"
    if hasattr(parent_profile, "position"):
        parent_profile.position = "Инженер"

    parent_profile.full_clean()
    parent_profile.save()

    return user, parent_profile


def create_admin_user(
    *,
    email: str = "admin@example.com",
    password: str = "TestPass123!",
):
    user = create_user(
        email=email,
        password=password,
        registration_type="teacher",
        is_staff=True,
        is_superuser=False,
    )
    create_profile(
        user=user,
        email=email,
        first_name="Админ",
        last_name="Системный",
        patronymic="",
    )
    assign_role(user=user, code=ROLE_ADMIN)
    return user
