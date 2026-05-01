from __future__ import annotations

from datetime import date

from apps.education.models import EducationPeriod
from apps.education.tests.factories.academic_year import create_academic_year
from apps.education.tests.factories.common import education_period_counter


def create_education_period(
    *,
    academic_year=None,
    name: str | None = None,
    code: str | None = None,
    period_type=EducationPeriod.PeriodTypeChoices.SEMESTER,
    sequence: int = 1,
    start_date=date(2025, 9, 1),
    end_date=date(2025, 12, 31),
    is_current: bool = False,
    is_active: bool = True,
):
    """Создаёт тестовый учебный период."""

    index = next(education_period_counter)

    if academic_year is None:
        academic_year = create_academic_year()

    if name is None:
        name = f"Период {index}"

    if code is None:
        code = f"PERIOD-{index}"

    return EducationPeriod.objects.create(
        academic_year=academic_year,
        name=name,
        code=code,
        period_type=period_type,
        sequence=sequence,
        start_date=start_date,
        end_date=end_date,
        is_current=is_current,
        is_active=is_active,
    )
