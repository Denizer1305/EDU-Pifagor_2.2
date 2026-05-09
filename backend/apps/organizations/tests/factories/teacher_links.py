from __future__ import annotations

from datetime import date

from apps.organizations.models import TeacherOrganization, TeacherSubject
from apps.organizations.tests.factories.organization import create_organization
from apps.organizations.tests.factories.subject import create_subject
from apps.organizations.tests.factories.users import create_teacher_user


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
    """Создаёт тестовую связь преподавателя с организацией."""

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
    """Создаёт тестовую связь преподавателя с предметом."""

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
