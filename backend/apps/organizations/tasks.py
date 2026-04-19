from __future__ import annotations

from datetime import date

from celery import shared_task
from django.db import transaction
from django.db.models import Count, Q
from django.utils import timezone

from apps.organizations.models import (
    Department,
    Group,
    GroupCurator,
    Organization,
    Subject,
    TeacherOrganization,
    TeacherSubject,
)

import logging


logger = logging.getLogger(__name__)


@shared_task
def deactivate_expired_teacher_organization_links() -> dict:
    """
    Деактивирует связи преподавателей с организациями,
    если срок действия связи уже завершён.

    Безопасность:
    - изменяются только активные записи;
    - затрагиваются только связи, у которых ends_at < сегодня или ends_at == сегодня.
    """
    today = timezone.localdate()

    with transaction.atomic():
        updated_count = TeacherOrganization.objects.filter(
            is_active=True,
            ends_at__isnull=False,
            ends_at__lte=today,
        ).update(is_active=False)

    logger.info(
        "Завершена деактивация просроченных связей преподавателей с организациями. "
        "updated_count=%s, date=%s",
        updated_count,
        today,
    )

    return {
        "updated_count": updated_count,
        "date": str(today),
    }


@shared_task
def deactivate_expired_primary_group_curators() -> dict:
    """
    Снимает признак основного куратора у записей,
    срок действия которых уже завершился.

    Безопасность:
    - не удаляет данные;
    - не меняет преподавателя или группу;
    - снимает только флаг is_primary у завершённых связей.
    """
    today = timezone.localdate()

    with transaction.atomic():
        updated_count = GroupCurator.objects.filter(
            is_primary=True,
            ends_at__isnull=False,
            ends_at__lte=today,
        ).update(is_primary=False)

    logger.info(
        "Завершено снятие primary-статуса у завершённых кураторов групп. "
        "updated_count=%s, date=%s",
        updated_count,
        today,
    )

    return {
        "updated_count": updated_count,
        "date": str(today),
    }


@shared_task
def log_organizations_structure_summary() -> dict:
    """
    Формирует и логирует сводку по организационной структуре платформы.

    Используется для:
    - технического мониторинга;
    - диагностики наполненности системы;
    - эксплуатационного аудита.
    """
    summary = {
        "organizations_total": Organization.objects.count(),
        "organizations_active": Organization.objects.filter(is_active=True).count(),
        "departments_total": Department.objects.count(),
        "groups_total": Group.objects.count(),
        "groups_active": Group.objects.filter(is_active=True).count(),
        "subjects_total": Subject.objects.count(),
        "teacher_organizations_total": TeacherOrganization.objects.count(),
        "teacher_organizations_active": TeacherOrganization.objects.filter(is_active=True).count(),
        "teacher_subjects_total": TeacherSubject.objects.count(),
        "group_curators_total": GroupCurator.objects.count(),
        "group_curators_primary": GroupCurator.objects.filter(is_primary=True).count(),
        "generated_at": timezone.now().isoformat(),
    }

    logger.info("Сводка по организационной структуре платформы: %s", summary)
    return summary


@shared_task
def log_organizations_integrity_report() -> dict:
    """
    Формирует и логирует отчёт по потенциально проблемным местам
    в организационной структуре.

    Эта задача ничего не исправляет автоматически.
    Она только сообщает о данных, которые требуют внимания администратора.
    """
    organizations_without_departments = (
        Organization.objects.annotate(
            departments_count=Count("departments"),
        )
        .filter(departments_count=0)
        .count()
    )

    groups_without_curators = (
        Group.objects.annotate(
            curators_count=Count("curators"),
        )
        .filter(curators_count=0)
        .count()
    )

    teachers_without_subjects = (
        TeacherOrganization.objects.filter(is_active=True)
        .values("teacher_id")
        .annotate(subjects_count=Count("teacher__teacher_subjects"))
        .filter(subjects_count=0)
        .count()
    )

    teachers_without_active_organizations = (
        TeacherSubject.objects.values("teacher_id")
        .annotate(
            active_orgs_count=Count(
                "teacher__teacher_organizations",
                filter=Q(teacher__teacher_organizations__is_active=True),
            )
        )
        .filter(active_orgs_count=0)
        .count()
    )

    report = {
        "organizations_without_departments": organizations_without_departments,
        "groups_without_curators": groups_without_curators,
        "teachers_without_subjects": teachers_without_subjects,
        "teachers_without_active_organizations": teachers_without_active_organizations,
        "generated_at": timezone.now().isoformat(),
    }

    logger.warning("Отчёт по целостности организационной структуры: %s", report)
    return report
