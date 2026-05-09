from __future__ import annotations

from datetime import date

from apps.education.models import GroupSubject
from apps.education.tests.factories.academic_year import create_academic_year
from apps.education.tests.factories.education_period import create_education_period
from apps.organizations.tests.factories import create_group, create_subject


def create_group_subject(
    *,
    group=None,
    subject=None,
    academic_year=None,
    period=None,
    planned_hours: int = 72,
    contact_hours: int = 48,
    independent_hours: int = 24,
    assessment_type=GroupSubject.AssessmentTypeChoices.EXAM,
    is_required: bool = True,
    is_active: bool = True,
):
    """Создаёт тестовый учебный предмет группы."""

    if academic_year is None:
        academic_year = create_academic_year()

    if period is None:
        period = create_education_period(
            academic_year=academic_year,
            start_date=academic_year.start_date,
            end_date=date(2025, 12, 31),
        )

    if group is None:
        group = create_group()

    if subject is None:
        subject = create_subject()

    return GroupSubject.objects.create(
        group=group,
        subject=subject,
        academic_year=academic_year,
        period=period,
        planned_hours=planned_hours,
        contact_hours=contact_hours,
        independent_hours=independent_hours,
        assessment_type=assessment_type,
        is_required=is_required,
        is_active=is_active,
    )
