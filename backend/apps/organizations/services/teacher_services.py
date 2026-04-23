from __future__ import annotations

import logging

from django.core.exceptions import ValidationError
from django.db import transaction

from apps.organizations.models import (
    Organization,
    Subject,
    TeacherOrganization,
    TeacherSubject,
)
from apps.users.constants import ROLE_TEACHER

logger = logging.getLogger(__name__)


def _clean_str(value: str | None) -> str:
    return (value or "").strip()


def _user_has_teacher_role(user) -> bool:
    if not user or not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    if getattr(user, "registration_type", "") == "teacher":
        return True

    if not hasattr(user, "user_roles"):
        return False

    queryset = user.user_roles.filter(role__code=ROLE_TEACHER)
    model_fields = {field.name for field in queryset.model._meta.get_fields()}
    if "is_active" in model_fields:
        queryset = queryset.filter(is_active=True)

    return queryset.exists()


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
    logger.info(
        "assign_teacher_to_organization started teacher_id=%s organization_id=%s",
        teacher.id,
        organization.id,
    )

    if not _user_has_teacher_role(teacher):
        raise ValidationError(
            {"teacher": "Связь с организацией можно создать только для преподавателя."}
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
            "remove_teacher_from_organization skipped teacher_id=%s organization_id=%s not_found",
            teacher.id,
            organization.id,
        )
        return

    link.is_active = False
    link.is_primary = False
    link.full_clean()
    link.save(update_fields=(
        "is_active",
        "is_primary",
        "updated_at",
    ))

    logger.info("remove_teacher_from_organization completed link_id=%s", link.id)


@transaction.atomic
def set_primary_teacher_organization(
    *,
    teacher,
    organization: Organization,
) -> TeacherOrganization:
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
            {"organization": "У преподавателя нет связи с указанной организацией."}
        )

    if not link.is_active:
        raise ValidationError(
            {"organization": "Нельзя сделать основной неактивную связь преподавателя с организацией."}
        )

    TeacherOrganization.objects.filter(
        teacher=teacher,
        is_primary=True,
        is_active=True,
    ).exclude(pk=link.pk).update(is_primary=False)

    link.is_primary = True
    link.full_clean()
    link.save(update_fields=(
        "is_primary",
        "updated_at",
    ))

    logger.info("set_primary_teacher_organization completed link_id=%s", link.id)
    return link


@transaction.atomic
def assign_teacher_subject(
    *,
    teacher,
    subject: Subject,
    is_primary: bool = False,
    is_active: bool = True,
) -> TeacherSubject:
    logger.info("assign_teacher_subject started teacher_id=%s subject_id=%s", teacher.id, subject.id)

    if not _user_has_teacher_role(teacher):
        raise ValidationError(
            {"teacher": "Связь с предметом можно создать только для преподавателя."}
        )

    link, created = TeacherSubject.objects.get_or_create(
        teacher=teacher,
        subject=subject,
        defaults={
            "is_primary": is_primary,
            "is_active": is_active,
        },
    )

    if not created:
        link.is_primary = is_primary
        link.is_active = is_active

    if is_primary and is_active:
        TeacherSubject.objects.filter(
            teacher=teacher,
            is_primary=True,
            is_active=True,
        ).exclude(pk=link.pk).update(is_primary=False)

    link.full_clean()
    link.save()
    logger.info("assign_teacher_subject completed link_id=%s", link.id)
    return link


@transaction.atomic
def remove_teacher_subject(
    *,
    teacher,
    subject: Subject,
) -> None:
    logger.info("remove_teacher_subject started teacher_id=%s subject_id=%s", teacher.id, subject.id)

    link = TeacherSubject.objects.filter(
        teacher=teacher,
        subject=subject,
    ).first()

    if not link:
        logger.info(
            "remove_teacher_subject skipped teacher_id=%s subject_id=%s not_found",
            teacher.id,
            subject.id,
        )
        return

    link.is_active = False
    link.is_primary = False
    link.full_clean()
    link.save(update_fields=(
        "is_active",
        "is_primary",
        "updated_at",
    ))

    logger.info("remove_teacher_subject completed link_id=%s", link.id)
