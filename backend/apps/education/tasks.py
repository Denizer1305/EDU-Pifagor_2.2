from __future__ import annotations

import logging

from celery import shared_task
from django.db import models, transaction
from django.db.models import Count
from django.utils import timezone

from apps.education.models import (
    AcademicYear,
    EducationPeriod,
    GroupSubject,
    StudentGroupEnrollment,
    TeacherGroupSubject,
)

logger = logging.getLogger(__name__)


@shared_task
def sync_current_academic_year() -> dict:
    """
    Синхронизирует текущий учебный год по текущей дате.

    Логика:
    - активным текущим может быть только один учебный год;
    - выбирается активный учебный год, в диапазон которого попадает текущая дата;
    - если таких несколько, выбирается самый поздний по start_date.
    """
    today = timezone.localdate()

    current_qs = AcademicYear.objects.filter(
        is_active=True,
        start_date__lte=today,
        end_date__gte=today,
    ).order_by("-start_date")

    current_year = current_qs.first()

    with transaction.atomic():
        AcademicYear.objects.filter(is_current=True).update(is_current=False)

        updated_id = None
        if current_year:
            current_year.is_current = True
            current_year.full_clean()
            current_year.save(update_fields=("is_current", "updated_at"))
            updated_id = current_year.id

    result = {
        "date": str(today),
        "current_academic_year_id": updated_id,
        "matched_years_count": current_qs.count(),
    }

    logger.info("Синхронизация текущего учебного года завершена: %s", result)
    return result


@shared_task
def sync_current_education_periods() -> dict:
    """
    Синхронизирует текущие учебные периоды по текущей дате.

    Логика:
    - внутри каждого учебного года текущим может быть только один период;
    - выбирается активный период, в диапазон которого попадает текущая дата;
    - если таких несколько, выбирается первый по sequence.
    """
    today = timezone.localdate()
    updated_count = 0

    with transaction.atomic():
        for academic_year in AcademicYear.objects.filter(is_active=True):
            periods_qs = EducationPeriod.objects.filter(
                academic_year=academic_year,
                is_active=True,
                start_date__lte=today,
                end_date__gte=today,
            ).order_by("sequence", "start_date")

            current_period = periods_qs.first()

            EducationPeriod.objects.filter(
                academic_year=academic_year,
                is_current=True,
            ).update(is_current=False)

            if current_period:
                current_period.is_current = True
                current_period.full_clean()
                current_period.save(update_fields=("is_current", "updated_at"))
                updated_count += 1

    result = {
        "date": str(today),
        "updated_count": updated_count,
    }

    logger.info("Синхронизация текущих учебных периодов завершена: %s", result)
    return result


@shared_task
def deactivate_expired_teacher_group_subject_assignments() -> dict:
    """
    Деактивирует завершенные закрепления преподавателей за предметами групп.

    Безопасность:
    - данные не удаляются;
    - история не теряется;
    - снимаются только is_active и is_primary у завершённых назначений.
    """
    today = timezone.localdate()

    with transaction.atomic():
        updated_count = TeacherGroupSubject.objects.filter(
            is_active=True,
            ends_at__isnull=False,
            ends_at__lte=today,
        ).update(
            is_active=False,
            is_primary=False,
        )

    result = {
        "date": str(today),
        "updated_count": updated_count,
    }

    logger.info(
        "Деактивация завершённых закреплений преподавателей завершена: %s", result
    )
    return result


@shared_task
def log_education_integrity_report() -> dict:
    """
    Формирует и логирует отчёт по целостности академической структуры.

    Эта задача ничего не исправляет автоматически.
    Она только помогает находить потенциально проблемные места.
    """
    groups_without_subjects = GroupSubject.objects.values("group_id").distinct().count()

    active_enrollments_without_journal_number = StudentGroupEnrollment.objects.filter(
        status=StudentGroupEnrollment.StatusChoices.ACTIVE,
        journal_number__isnull=True,
    ).count()

    periods_without_group_subjects = (
        EducationPeriod.objects.annotate(
            group_subjects_count=Count("group_subjects"),
        )
        .filter(group_subjects_count=0)
        .count()
    )

    group_subjects_without_teacher = (
        GroupSubject.objects.annotate(
            assignments_count=Count("teacher_assignments"),
        )
        .filter(assignments_count=0)
        .count()
    )

    active_teacher_assignments_without_org_link = (
        TeacherGroupSubject.objects.filter(is_active=True)
        .exclude(
            teacher__teacher_organizations__organization_id=models.F(
                "group_subject__group__organization_id"
            ),
            teacher__teacher_organizations__is_active=True,
        )
        .count()
    )

    report = {
        "generated_at": timezone.now().isoformat(),
        "groups_with_subject_records": groups_without_subjects,
        "active_enrollments_without_journal_number": active_enrollments_without_journal_number,
        "periods_without_group_subjects": periods_without_group_subjects,
        "group_subjects_without_teacher": group_subjects_without_teacher,
        "active_teacher_assignments_without_org_link": active_teacher_assignments_without_org_link,
    }

    logger.warning("Отчёт по целостности академической структуры: %s", report)
    return report
