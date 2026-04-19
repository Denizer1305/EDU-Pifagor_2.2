from __future__ import annotations

from itertools import count

from apps.organizations.models import (
    Department,
    Group,
    GroupCurator,
    Organization,
    OrganizationType,
    Subject,
    SubjectCategory,
    TeacherOrganization,
    TeacherSubject,
)
from apps.users.constants import ROLE_TEACHER
from apps.users.tests.factories import assign_role, create_profile, create_user


organization_type_counter = count(1)
organization_counter = count(1)
department_counter = count(1)
subject_category_counter = count(1)
subject_counter = count(1)
group_counter = count(1)
teacher_counter = count(1)
non_teacher_counter = count(1)


def create_organization_type(
    *,
    code: str | None = None,
    name: str | None = None,
    description: str = "",
    is_active: bool = True,
):
    index = next(organization_type_counter)

    if code is None:
        code = f"organization_type_{index}"
    if name is None:
        name = f"Тип организации {index}"

    return OrganizationType.objects.create(
        code=code,
        name=name,
        description=description,
        is_active=is_active,
    )


def create_organization(
    *,
    organization_type=None,
    name: str | None = None,
    short_name: str | None = None,
    city: str = "Москва",
    is_active: bool = True,
):
    index = next(organization_counter)

    if organization_type is None:
        organization_type = create_organization_type()

    if name is None:
        name = f"Организация {index}"
    if short_name is None:
        short_name = f"Орг{index}"

    return Organization.objects.create(
        type=organization_type,
        name=name,
        short_name=short_name,
        city=city,
        is_active=is_active,
    )


def create_department(
    *,
    organization=None,
    name: str | None = None,
    short_name: str | None = None,
    is_active: bool = True,
):
    index = next(department_counter)

    if organization is None:
        organization = create_organization()

    if name is None:
        name = f"Отделение {index}"
    if short_name is None:
        short_name = f"Отд{index}"

    return Department.objects.create(
        organization=organization,
        name=name,
        short_name=short_name,
        is_active=is_active,
    )


def create_subject_category(
    *,
    code: str | None = None,
    name: str | None = None,
    is_active: bool = True,
):
    index = next(subject_category_counter)

    if code is None:
        code = f"subject_category_{index}"
    if name is None:
        name = f"Категория предметов {index}"

    return SubjectCategory.objects.create(
        code=code,
        name=name,
        is_active=is_active,
    )


def create_subject(
    *,
    category=None,
    name: str | None = None,
    short_name: str | None = None,
    is_active: bool = True,
):
    index = next(subject_counter)

    if category is None:
        category = create_subject_category()

    if name is None:
        name = f"Предмет {index}"
    if short_name is None:
        short_name = f"Предмет {index}"

    return Subject.objects.create(
        category=category,
        name=name,
        short_name=short_name,
        is_active=is_active,
    )


def create_group(
    *,
    organization=None,
    department=None,
    name: str | None = None,
    code: str | None = None,
    study_form: str = Group.StudyFormChoices.FULL_TIME,
    status: str = Group.StatusChoices.ACTIVE,
    is_active: bool = True,
):
    index = next(group_counter)

    if organization is None:
        organization = create_organization()

    if name is None:
        name = f"Группа {index}"
    if code is None:
        code = f"GROUP-{index}"

    return Group.objects.create(
        organization=organization,
        department=department,
        name=name,
        code=code,
        study_form=study_form,
        status=status,
        is_active=is_active,
    )


def create_teacher_user(
    *,
    email: str | None = None,
    password: str = "TestPass123!",
):
    index = next(teacher_counter)

    if email is None:
        email = f"teacher_org_{index}@example.com"

    user = create_user(email=email, password=password)
    create_profile(
        user=user,
        email=email,
        first_name="Мария",
        last_name=f"Петрова{index}",
        patronymic="Игоревна",
    )
    assign_role(user=user, code=ROLE_TEACHER)
    return user


def create_non_teacher_user(
    *,
    email: str | None = None,
    password: str = "TestPass123!",
):
    index = next(non_teacher_counter)

    if email is None:
        email = f"simple_org_{index}@example.com"

    user = create_user(email=email, password=password)
    create_profile(
        user=user,
        email=email,
        first_name="Иван",
        last_name=f"Сидоров{index}",
        patronymic="Петрович",
    )
    return user


def create_group_curator(
    *,
    group=None,
    teacher=None,
    is_primary: bool = True,
):
    if group is None:
        group = create_group()
    if teacher is None:
        teacher = create_teacher_user()

    return GroupCurator.objects.create(
        group=group,
        teacher=teacher,
        is_primary=is_primary,
    )


def create_teacher_organization(
    *,
    teacher=None,
    organization=None,
    is_primary: bool = False,
):
    if teacher is None:
        teacher = create_teacher_user()
    if organization is None:
        organization = create_organization()

    return TeacherOrganization.objects.create(
        teacher=teacher,
        organization=organization,
        is_primary=is_primary,
    )


def create_teacher_subject(
    *,
    teacher=None,
    subject=None,
    is_primary: bool = False,
):
    if teacher is None:
        teacher = create_teacher_user()
    if subject is None:
        subject = create_subject()

    return TeacherSubject.objects.create(
        teacher=teacher,
        subject=subject,
        is_primary=is_primary,
    )
