from __future__ import annotations

from datetime import date

from apps.education.models import TeacherGroupSubject
from apps.education.tests.factories.group_subject import create_group_subject
from apps.education.tests.factories.users import create_teacher_user
from apps.organizations.tests.factories import (
    create_teacher_organization,
    create_teacher_subject,
)


def create_teacher_group_subject(
    *,
    teacher=None,
    group_subject=None,
    role=TeacherGroupSubject.RoleChoices.PRIMARY,
    is_primary: bool = True,
    is_active: bool = True,
    planned_hours: int = 72,
    starts_at=date(2025, 9, 1),
    ends_at=date(2025, 12, 31),
):
    """Создаёт тестовую связь преподавателя с предметом группы."""

    if teacher is None:
        teacher = create_teacher_user()

    if group_subject is None:
        group_subject = create_group_subject()

    create_teacher_organization(
        teacher=teacher,
        organization=group_subject.group.organization,
        is_primary=True,
        is_active=True,
    )
    create_teacher_subject(
        teacher=teacher,
        subject=group_subject.subject,
        is_primary=True,
        is_active=True,
    )

    return TeacherGroupSubject.objects.create(
        teacher=teacher,
        group_subject=group_subject,
        role=role,
        is_primary=is_primary,
        is_active=is_active,
        planned_hours=planned_hours,
        starts_at=starts_at,
        ends_at=ends_at,
    )
