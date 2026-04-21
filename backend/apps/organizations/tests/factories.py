from __future__ import annotations

from datetime import date
from itertools import count

from django.contrib.auth import get_user_model

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
from apps.users.services.profile_services import ensure_role_profile, get_or_create_base_profile
from apps.users.tests.factories import assign_role

User = get_user_model()


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
    description: str = "",
    city: str = "Москва",
    address: str = "",
    phone: str = "",
    email: str = "",
    website: str = "",
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
        description=description,
        city=city,
        address=address,
        phone=phone,
        email=email,
        website=website,
        is_active=is_active,
    )


def create_department(
    *,
    organization=None,
    name: str | None = None,
    short_name: str | None = None,
    description: str = "",
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
        description=description,
        is_active=is_active,
    )


def create_subject_category(
    *,
    code: str | None = None,
    name: str | None = None,
    description: str = "",
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
        description=description,
        is_active=is_active,
    )


def create_subject(
    *,
    category=None,
    name: str | None = None,
    short_name: str | None = None,
    description: str = "",
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
        description=description,
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
    course_number: int | None = None,
    admission_year: int | None = None,
    graduation_year: int | None = None,
    academic_year: str = "",
    description: str = "",
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
        course_number=course_number,
        admission_year=admission_year,
        graduation_year=graduation_year,
        academic_year=academic_year,
        description=description,
        is_active=is_active,
    )


def _build_user(
    *,
    email: str,
    password: str,
    registration_type: str,
    first_name: str,
    last_name: str,
    patronymic: str,
):
    user = User.objects.create_user(
        email=email,
        password=password,
        registration_type=registration_type,
    )

    profile = get_or_create_base_profile(user)
    profile.first_name = first_name
    profile.last_name = last_name
    profile.patronymic = patronymic
    profile.full_clean()
    profile.save()

    ensure_role_profile(user)
    return user


def create_teacher_user(
    *,
    email: str | None = None,
    password: str = "TestPass123!",
):
    index = next(teacher_counter)

    if email is None:
        email = f"teacher_org_{index}@example.com"

    user = _build_user(
        email=email,
        password=password,
        registration_type="teacher",
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
    registration_type: str = "student",
):
    index = next(non_teacher_counter)

    if email is None:
        email = f"simple_org_{index}@example.com"

    return _build_user(
        email=email,
        password=password,
        registration_type=registration_type,
        first_name="Иван",
        last_name=f"Сидоров{index}",
        patronymic="Петрович",
    )


def create_group_curator(
    *,
    group=None,
    teacher=None,
    is_primary: bool = True,
    is_active: bool = True,
    starts_at: date | None = None,
    ends_at: date | None = None,
    notes: str = "",
):
    if group is None:
        group = create_group()
    if teacher is None:
        teacher = create_teacher_user()

    return GroupCurator.objects.create(
        group=group,
        teacher=teacher,
        is_primary=is_primary,
        is_active=is_active,
        starts_at=starts_at,
        ends_at=ends_at,
        notes=notes,
    )


def create_teacher_organization(
    *,
    teacher=None,
    organization=None,
    position: str = "",
    employment_type: str = TeacherOrganization.EmploymentTypeChoices.MAIN,
    is_primary: bool = False,
    is_active: bool = True,
    starts_at: date | None = None,
    ends_at: date | None = None,
    notes: str = "",
):
    if teacher is None:
        teacher = create_teacher_user()
    if organization is None:
        organization = create_organization()

    return TeacherOrganization.objects.create(
        teacher=teacher,
        organization=organization,
        position=position,
        employment_type=employment_type,
        is_primary=is_primary,
        is_active=is_active,
        starts_at=starts_at,
        ends_at=ends_at,
        notes=notes,
    )


def create_teacher_subject(
    *,
    teacher=None,
    subject=None,
    is_primary: bool = False,
    is_active: bool = True,
):
    if teacher is None:
        teacher = create_teacher_user()
    if subject is None:
        subject = create_subject()

    return TeacherSubject.objects.create(
        teacher=teacher,
        subject=subject,
        is_primary=is_primary,
        is_active=is_active,
    )


def activate_teacher_registration_code(
    organization: Organization,
    raw_code: str = "TEACHER-CODE-123",
    *,
    expires_at=None,
) -> Organization:
    organization.set_teacher_registration_code(raw_code=raw_code, expires_at=expires_at)
    organization.save()
    return organization


def activate_group_join_code(
    group: Group,
    raw_code: str = "GROUP-CODE-123",
    *,
    expires_at=None,
) -> Group:
    group.set_join_code(raw_code=raw_code, expires_at=expires_at)
    group.save()
    return group
