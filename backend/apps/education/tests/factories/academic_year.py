from __future__ import annotations

from datetime import date

from apps.education.models import AcademicYear
from apps.education.tests.factories.common import academic_year_counter


def create_academic_year(
    *,
    name: str | None = None,
    start_date=date(2025, 9, 1),
    end_date=date(2026, 6, 30),
    is_current: bool = False,
    is_active: bool = True,
):
    """Создаёт тестовый учебный год."""

    index = next(academic_year_counter)

    if name is None:
        start_year = 2024 + index
        end_year = start_year + 1
        name = f"{start_year}/{end_year}"

    return AcademicYear.objects.create(
        name=name,
        start_date=start_date,
        end_date=end_date,
        is_current=is_current,
        is_active=is_active,
    )
