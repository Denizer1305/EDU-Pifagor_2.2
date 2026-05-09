from __future__ import annotations

from datetime import date

from apps.education.models import StudentGroupEnrollment
from apps.education.tests.factories.academic_year import create_academic_year
from apps.education.tests.factories.users import create_student_user
from apps.organizations.tests.factories import create_group


def create_student_group_enrollment(
    *,
    student=None,
    group=None,
    academic_year=None,
    enrollment_date=date(2025, 9, 1),
    completion_date=None,
    status=StudentGroupEnrollment.StatusChoices.ACTIVE,
    is_primary: bool = True,
    journal_number: int | None = 1,
):
    """Создаёт тестовое зачисление студента в учебную группу."""

    if student is None:
        student = create_student_user()

    if group is None:
        group = create_group()

    if academic_year is None:
        academic_year = create_academic_year()

    return StudentGroupEnrollment.objects.create(
        student=student,
        group=group,
        academic_year=academic_year,
        enrollment_date=enrollment_date,
        completion_date=completion_date,
        status=status,
        is_primary=is_primary,
        journal_number=journal_number,
    )
