from __future__ import annotations

from datetime import date

from apps.organizations.models import Group, GroupCurator
from apps.organizations.tests.factories.counters import group_counter
from apps.organizations.tests.factories.organization import create_organization
from apps.organizations.tests.factories.users import create_teacher_user


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
    """Создаёт тестовую учебную группу."""

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
    """Создаёт тестовую связь куратора с группой."""

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
