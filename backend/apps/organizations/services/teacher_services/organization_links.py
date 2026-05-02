from __future__ import annotations

import logging

from django.core.exceptions import ValidationError
from django.db import transaction

from apps.organizations.models import Organization, TeacherOrganization
from apps.organizations.services.teacher_services.common import (
    _clean_str,
    _user_has_teacher_role,
)

logger = logging.getLogger(__name__)


@transaction.atomic
def assign_teacher_to_organization(
    *,
    teacher,
    organization: Organization,
    position: str = "",
    employment_type: str = TeacherOrganization.EmploymentTypeChoices.MAIN,
    is_primary: bool = False,
    starts_at=None,
    ends_at=None,
    notes: str = "",
    is_active: bool = True,
) -> TeacherOrganization:
    """Создаёт или обновляет связь преподавателя с организацией."""

    logger.info(
        "assign_teacher_to_organization started teacher_id=%s organization_id=%s",
        teacher.id,
        organization.id,
    )

    if not _user_has_teacher_role(teacher):
        raise ValidationError(
            {
                "teacher": (
                    "Связь с организацией можно создать только для преподавателя."
                )
            }
        )

    link, created = TeacherOrganization.objects.get_or_create(
        teacher=teacher,
        organization=organization,
        defaults={
            "position": _clean_str(position),
            "employment_type": employment_type,
            "is_primary": is_primary,
            "starts_at": starts_at,
            "ends_at": ends_at,
            "notes": _clean_str(notes),
            "is_active": is_active,
        },
    )

    if not created:
        link.position = _clean_str(position)
        link.employment_type = employment_type
        link.is_primary = is_primary
        link.starts_at = starts_at
        link.ends_at = ends_at
        link.notes = _clean_str(notes)
        link.is_active = is_active

    if is_primary and is_active:
        TeacherOrganization.objects.filter(
            teacher=teacher,
            is_primary=True,
            is_active=True,
        ).exclude(pk=link.pk).update(is_primary=False)

    link.full_clean()
    link.save()

    logger.info("assign_teacher_to_organization completed link_id=%s", link.id)
    return link


@transaction.atomic
def remove_teacher_from_organization(
    *,
    teacher,
    organization: Organization,
) -> None:
    """Деактивирует связь преподавателя с организацией."""

    logger.info(
        "remove_teacher_from_organization started teacher_id=%s organization_id=%s",
        teacher.id,
        organization.id,
    )

    link = TeacherOrganization.objects.filter(
        teacher=teacher,
        organization=organization,
    ).first()

    if not link:
        logger.info(
            (
                "remove_teacher_from_organization skipped "
                "teacher_id=%s organization_id=%s not_found"
            ),
            teacher.id,
            organization.id,
        )
        return

    link.is_active = False
    link.is_primary = False
    link.full_clean()
    link.save(
        update_fields=(
            "is_active",
            "is_primary",
            "updated_at",
        )
    )

    logger.info("remove_teacher_from_organization completed link_id=%s", link.id)


@transaction.atomic
def set_primary_teacher_organization(
    *,
    teacher,
    organization: Organization,
) -> TeacherOrganization:
    """Делает организацию основной для преподавателя."""

    logger.info(
        "set_primary_teacher_organization started teacher_id=%s organization_id=%s",
        teacher.id,
        organization.id,
    )

    link = TeacherOrganization.objects.filter(
        teacher=teacher,
        organization=organization,
    ).first()

    if not link:
        raise ValidationError(
            {"organization": ("У преподавателя нет связи с указанной организацией.")}
        )

    if not link.is_active:
        raise ValidationError(
            {
                "organization": (
                    "Нельзя сделать основной неактивную связь преподавателя "
                    "с организацией."
                )
            }
        )

    TeacherOrganization.objects.filter(
        teacher=teacher,
        is_primary=True,
        is_active=True,
    ).exclude(pk=link.pk).update(is_primary=False)

    link.is_primary = True
    link.full_clean()
    link.save(
        update_fields=(
            "is_primary",
            "updated_at",
        )
    )

    logger.info("set_primary_teacher_organization completed link_id=%s", link.id)
    return link
