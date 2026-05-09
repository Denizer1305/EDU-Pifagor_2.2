from __future__ import annotations

from apps.schedule.constants import BatchStatus, ImportSourceType
from apps.schedule.models import ScheduleImportBatch
from apps.schedule.tests.factories.course import create_course


def batch_status(name: str, fallback: str) -> str:
    return getattr(BatchStatus, name, fallback)


def create_schedule_import_batch(**kwargs) -> ScheduleImportBatch:
    course = kwargs.pop("course", None) or create_course()

    defaults = {
        "organization": kwargs.pop("organization", course.organization),
        "academic_year": kwargs.pop("academic_year", course.academic_year),
        "education_period": kwargs.pop("education_period", course.period),
        "source_type": kwargs.pop("source_type", ImportSourceType.MANUAL),
        "status": kwargs.pop("status", BatchStatus.PENDING),
        "imported_by": kwargs.pop("imported_by", None),
    }
    defaults.update(kwargs)

    return ScheduleImportBatch.objects.create(**defaults)
