from __future__ import annotations

from typing import Any

from django.utils import timezone

from apps.education.models import AcademicYear, EducationPeriod
from apps.organizations.models import Organization
from apps.schedule.constants import BatchStatus, GenerationSource, ImportSourceType
from apps.schedule.models import ScheduleGenerationBatch, ScheduleImportBatch
from apps.schedule.tests.factories.calendar import (
    create_academic_year,
    create_education_period,
)
from apps.schedule.tests.factories.context import next_number
from apps.schedule.tests.factories.course import create_organization
from apps.schedule.tests.factories.users import create_admin
from apps.users.models import User


def create_schedule_generation_batch(
    *,
    organization: Organization | None = None,
    academic_year: AcademicYear | None = None,
    education_period: EducationPeriod | None = None,
    name: str | None = None,
    source: str = GenerationSource.PATTERNS,
    status: str = BatchStatus.PENDING,
    generated_by: User | None = None,
    dry_run: bool = True,
    **extra_fields: Any,
) -> ScheduleGenerationBatch:
    number = next_number()
    organization = organization or create_organization()
    academic_year = academic_year or create_academic_year()
    education_period = education_period or create_education_period(
        academic_year=academic_year,
    )
    generated_by = generated_by or create_admin()

    return ScheduleGenerationBatch.objects.create(
        organization=organization,
        academic_year=academic_year,
        education_period=education_period,
        name=name or f"Генерация расписания {number}",
        source=source,
        status=status,
        generated_by=generated_by,
        dry_run=dry_run,
        **extra_fields,
    )


def create_schedule_import_batch(
    *,
    organization: Organization | None = None,
    academic_year: AcademicYear | None = None,
    education_period: EducationPeriod | None = None,
    source_type: str = ImportSourceType.MANUAL,
    status: str = BatchStatus.PENDING,
    imported_by: User | None = None,
    **extra_fields: Any,
) -> ScheduleImportBatch:
    organization = organization or create_organization()
    academic_year = academic_year or create_academic_year()
    education_period = education_period or create_education_period(
        academic_year=academic_year,
    )
    imported_by = imported_by or create_admin()

    return ScheduleImportBatch.objects.create(
        organization=organization,
        academic_year=academic_year,
        education_period=education_period,
        source_type=source_type,
        status=status,
        imported_by=imported_by,
        **extra_fields,
    )


def mark_batch_started(batch: ScheduleGenerationBatch | ScheduleImportBatch) -> None:
    batch.status = BatchStatus.RUNNING
    batch.started_at = timezone.now()
    batch.save(update_fields=("status", "started_at", "updated_at"))


def mark_batch_finished(batch: ScheduleGenerationBatch | ScheduleImportBatch) -> None:
    batch.status = BatchStatus.SUCCESS
    batch.finished_at = timezone.now()
    batch.save(update_fields=("status", "finished_at", "updated_at"))
