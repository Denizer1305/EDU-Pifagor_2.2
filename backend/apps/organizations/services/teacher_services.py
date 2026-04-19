from __future__ import annotations

import logging

from django.core.exceptions import ValidationError
from django.db import transaction

from apps.organizations.models import Organization, Subject, TeacherOrganization, TeacherSubject
from apps.users.constants import ROLE_TEACHER

logger = logging.getLogger(__name__)


def _user_has_teacher_role(user) -> bool:
    if not user or not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    if not hasattr(user, "user_roles"):
        return False

    return user.user_roles.filter(role__code=ROLE_TEACHER).exists()


@transaction.atomic
def assign_teacher_to_organization(
    *,
    teacher,
    organization: Organization,
    employment_type: str = TeacherOrganization.EmploymentTypeChoices.MAIN,
    is_primary: bool = False,
    starts_at=None,
    ends_at=None,
    notes: str = "",
    is_active: bool = True,
) -> TeacherOrganization:
    logger.info("assign_teacher_to_organization started teacher_id=%s organization_id=%s", teacher.id, organization.id)
    if not _user_has_teacher_role(teacher):
        raise ValidationError({"teacher": "Связь с организацией можно создать только для преподавателя."})

    (
        link, created,
    ) = TeacherOrganization.objects.get_or_create(
        teacher=teacher,
        organization=organization,
        defaults={
            "employment_type": employment_type,
            "is_primary": is_primary,
            "starts_at": starts_at,
            "ends_at": ends_at,
            "notes": notes.strip(),
            "is_active": is_active,
        },
    )

    if not created:
        link.employment_type = employment_type
        link.is_primary = is_primary
        link.starts_at = starts_at
        link.ends_at = ends_at
        link.notes = notes.strip()
        link.is_active = is_active

    if is_primary:
        TeacherOrganization.objects.filter(
            teacher=teacher,
            is_primary=True,
        ).exclude(pk=link.pk).update(is_primary=False)

    link.full_clean()
    link.save()
    logger.info("assign_teacher_to_organization completed link_id=%s", link.id)
    return link


@transaction.atomic
def remove_teacher_from_organization(*, teacher, organization: Organization) -> None:
    logger.info("remove_teacher_from_organization teacher_id=%s organization_id=%s", teacher.id, organization.id)
    TeacherOrganization.objects.filter(
        teacher=teacher,
        organization=organization,
    ).delete()


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
        raise ValidationError({"teacher": "Связь с предметом можно создать только для преподавателя."})

    (
        link, created,
    ) = TeacherSubject.objects.get_or_create(
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

    if is_primary:
        TeacherSubject.objects.filter(
            teacher=teacher,
            is_primary=True,
        ).exclude(pk=link.pk).update(is_primary=False)

    link.full_clean()
    link.save()
    logger.info("assign_teacher_subject completed link_id=%s", link.id)
    return link


@transaction.atomic
def remove_teacher_subject(*, teacher, subject: Subject) -> None:
    logger.info("remove_teacher_subject teacher_id=%s subject_id=%s", teacher.id, subject.id)
    TeacherSubject.objects.filter(
        teacher=teacher,
        subject=subject,
    ).delete()
