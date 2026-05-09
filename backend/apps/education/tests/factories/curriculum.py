from __future__ import annotations

from datetime import date

from apps.education.models import Curriculum, CurriculumItem
from apps.education.tests.factories.academic_year import create_academic_year
from apps.education.tests.factories.common import curriculum_counter
from apps.education.tests.factories.education_period import create_education_period
from apps.organizations.tests.factories import (
    create_department,
    create_organization,
    create_subject,
)


def create_curriculum(
    *,
    organization=None,
    department=None,
    academic_year=None,
    code: str | None = None,
    name: str | None = None,
    total_hours: int | None = 144,
    is_active: bool = True,
):
    """Создаёт тестовый учебный план."""

    index = next(curriculum_counter)

    if organization is None:
        organization = create_organization()

    if academic_year is None:
        academic_year = create_academic_year()

    if department is None:
        department = create_department(organization=organization)

    if code is None:
        code = f"CURR-{index}"

    if name is None:
        name = f"Учебный план {index}"

    return Curriculum.objects.create(
        organization=organization,
        department=department,
        academic_year=academic_year,
        code=code,
        name=name,
        total_hours=total_hours,
        is_active=is_active,
    )


def create_curriculum_item(
    *,
    curriculum=None,
    period=None,
    subject=None,
    sequence: int = 1,
    planned_hours: int = 72,
    contact_hours: int = 48,
    independent_hours: int = 24,
    assessment_type=CurriculumItem.AssessmentTypeChoices.EXAM,
    is_required: bool = True,
    is_active: bool = True,
):
    """Создаёт тестовый элемент учебного плана."""

    if curriculum is None:
        curriculum = create_curriculum()

    if period is None:
        period = create_education_period(
            academic_year=curriculum.academic_year,
            start_date=curriculum.academic_year.start_date,
            end_date=date(2025, 12, 31),
        )

    if subject is None:
        subject = create_subject()

    return CurriculumItem.objects.create(
        curriculum=curriculum,
        period=period,
        subject=subject,
        sequence=sequence,
        planned_hours=planned_hours,
        contact_hours=contact_hours,
        independent_hours=independent_hours,
        assessment_type=assessment_type,
        is_required=is_required,
        is_active=is_active,
    )
