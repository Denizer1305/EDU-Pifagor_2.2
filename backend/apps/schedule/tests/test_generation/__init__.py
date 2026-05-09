from __future__ import annotations

from apps.schedule.constants import BatchStatus, GenerationSource
from apps.schedule.models import ScheduleGenerationBatch
from apps.schedule.tests.factories import create_course

COMPLETED_STATUS = getattr(BatchStatus, "COMPLETED", "completed")


_UNSET = object()


def create_schedule_generation_batch(
    *,
    pattern=None,
    dry_run: bool = True,
    education_period=_UNSET,
    **kwargs,
):
    if pattern is not None:
        organization = kwargs.pop("organization", pattern.organization)
        academic_year = kwargs.pop("academic_year", pattern.academic_year)

        if education_period is _UNSET:
            education_period = pattern.education_period
    else:
        course = create_course()
        organization = kwargs.pop("organization", course.organization)
        academic_year = kwargs.pop("academic_year", course.academic_year)

        if education_period is _UNSET:
            education_period = course.period

    defaults = {
        "organization": organization,
        "academic_year": academic_year,
        "education_period": education_period,
        "name": kwargs.pop("name", "Тестовая генерация расписания"),
        "source": kwargs.pop("source", GenerationSource.PATTERNS),
        "status": kwargs.pop("status", BatchStatus.PENDING),
        "generated_by": kwargs.pop("generated_by", None),
        "dry_run": kwargs.pop("dry_run", dry_run),
        "lessons_created": kwargs.pop("lessons_created", 0),
        "lessons_updated": kwargs.pop("lessons_updated", 0),
        "conflicts_count": kwargs.pop("conflicts_count", 0),
        "log": kwargs.pop("log", ""),
    }
    defaults.update(kwargs)

    return ScheduleGenerationBatch.objects.create(**defaults)
